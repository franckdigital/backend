"""
Service de synchronisation BIDIRECTIONNELLE entre Django (sav_pharmacie)
et WinDev (FacturationClient).

Deux sens :
  - WinDev → Django :
      QUI LIT ?  → Django lit la base MySQL « FacturationClient » (tables T_Client, T_Utilisateur, etc.)
      QUI ÉCRIT ? → Django écrit dans sa propre base « sav_pharmacie » (tables User, Pharmacie, Ticket, etc.)
      RÉSULTAT : les données WinDev (clients, techniciens, interventions) deviennent visibles dans l'app web.

  - Django → WinDev :
      QUI LIT ?  → Django lit sa propre base « sav_pharmacie » (tables Ticket, RapportIntervention, Pharmacie)
      QUI ÉCRIT ? → Django écrit dans la base MySQL « FacturationClient » (tables T_BesoinsClient, T_Client, T_DetailIntervention)
      RÉSULTAT : les données créées en ligne (tickets, rapports) deviennent visibles dans WinDev.

  Dans les deux cas, c'est TOUJOURS Django qui fait le travail (lecture + écriture).
  WinDev ne fait RIEN côté synchronisation — il continue de fonctionner normalement
  avec sa base MySQL comme d'habitude.

Synchronisation incrémentale : utilise SyncCursor pour ne traiter
que les enregistrements nouveaux/modifiés depuis le dernier cycle.
"""
import logging
import datetime as dt
from django.db import connections
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.pharmacies.models import Pharmacie
from apps.zones.models import TechnicienProfile, Region, Commune
from apps.tickets.models import Ticket
from apps.interventions.models import RapportIntervention
from .models import SyncLog, SyncCursor

User = get_user_model()
logger = logging.getLogger('windev_sync')


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def _windev_cursor():
    """Curseur lecture seule vers FacturationClient."""
    return connections['windev'].cursor()


def _windev_write_cursor():
    """Curseur écriture vers FacturationClient (pour Django→WinDev)."""
    return connections['windev'].cursor()


def _get_cursor(entity_type, direction):
    """Récupère ou crée le curseur de sync pour une entité."""
    cursor, _ = SyncCursor.objects.get_or_create(
        entity_type=entity_type,
        defaults={'direction': direction, 'last_synced_id': 0},
    )
    return cursor


def _log(direction, entity_type, synced, failed, errors, started):
    """Enregistre un log de sync."""
    SyncLog.objects.create(
        direction=direction, entity_type=entity_type,
        records_synced=synced, records_failed=failed,
        status='success' if failed == 0 else ('partial' if synced > 0 else 'failed'),
        error_details='\n'.join(errors[-50:]) if errors else '',
        started_at=started, completed_at=timezone.now(),
    )


# ═══════════════════════════════════════════════════════════
#  WINDEV → DJANGO  (lecture FacturationClient)
# ═══════════════════════════════════════════════════════════

def sync_clients_incremental():
    """
    ÉTAPE 2a — Sync incrémentale T_Client → User (pharmacie) + Pharmacie.

    Pour chaque client WinDev :
    1. Crée un User Django (username=pharma_wd_{IDClient}, password=sav_{IDClient}_temp)
       Le mot de passe n'est défini qu'à la première création (if created:).
    2. Crée ou met à jour la fiche Pharmacie liée à ce User.

    Incrémentale : ne traite que les clients avec IDClient > dernier_sync
    ou DateDernierModif >= dernière date de sync.
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []
    sc = _get_cursor('wd_client', 'windev_to_web')

    try:
        cursor = _windev_cursor()
        cursor.execute("""
            SELECT IDClient, NomClient, TelFixe, TelCel, Code_2ST,
                   AdresseGeo, EmailClient, NomResponsable, TelPharmacien,
                   SousContrat, IDLocalite, ActifOP, InterieurPays,
                   DateMaintenance, MontantContrat, telCel2
            FROM T_Client
            WHERE IDClient > %s OR DateDernierModif >= %s
            ORDER BY IDClient
        """, [sc.last_synced_id, sc.last_synced_at or '2000-01-01'])
        rows = cursor.fetchall()

        max_id = sc.last_synced_id
        for row in rows:
            try:
                (id_client, nom, tel_fixe, tel_cel, code_2st,
                 adresse, email, responsable, tel_resp,
                 sous_contrat, id_localite, actif, interieur,
                 date_maintenance, montant_contrat, tel_cel2) = row

                # --- Création du User Django pour ce client WinDev ---
                # Username : pharma_wd_{IDClient} (ex: pharma_wd_7)
                # Le mot de passe temporaire (sav_{IDClient}_temp) n'est défini
                # qu'à la PREMIÈRE création. Les syncs suivantes ne l'écrasent pas.
                username = f"pharma_wd_{id_client}"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'role': 'pharmacie',
                        'first_name': (nom or '')[:150],
                        'phone': tel_cel or tel_fixe or '',
                        'phone2': tel_cel2 or '',
                        'email': email or '',
                        'is_validated': True,
                    }
                )
                if created:
                    # Mot de passe temporaire — l'admin peut le changer via set_password
                    user.set_password(f"sav_{id_client}_temp")
                    user.save()

                # --- Résolution géographique ---
                # Trouver la commune Django via IDLocalite WinDev (code=WD-{IDLocalite})
                commune = None
                if id_localite:
                    commune = Commune.objects.filter(code=f"WD-{id_localite}").first()

                defaults_data = {
                    'nom_pharmacie': (nom or f'Pharmacie #{id_client}')[:150],
                    'code_2st': (code_2st or '')[:10],
                    'adresse': (adresse or '')[:255],
                    'nom_responsable': (responsable or '')[:100],
                    'tel_responsable': (tel_resp or tel_fixe or '')[:20],
                    'email_pharmacie': email or '',
                    'sous_contrat': bool(sous_contrat),
                    'interieur_pays': bool(interieur),
                    'date_maintenance': date_maintenance,
                    'commune': commune,
                }

                # --- Liaison User ↔ Pharmacie ---
                # On ne remplace PAS le user si la pharmacie a été associée
                # manuellement à un vrai compte (non auto-généré).
                existing = Pharmacie.objects.filter(windev_client_id=id_client).first()
                if existing:
                    if existing.user and not existing.user.username.startswith('pharma_wd_'):
                        pass  # Garder le vrai user associé manuellement
                    else:
                        defaults_data['user'] = user
                else:
                    defaults_data['user'] = user

                # --- Création ou mise à jour de la fiche Pharmacie ---
                Pharmacie.objects.update_or_create(
                    windev_client_id=id_client,
                    defaults=defaults_data,
                )
                synced += 1
                max_id = max(max_id, id_client)
            except Exception as e:
                failed += 1
                errors.append(f"Client {row[0]}: {e}")

        sc.last_synced_id = max_id
        sc.last_synced_at = timezone.now()
        sc.save()

    except Exception as e:
        logger.error(f"sync_clients_incremental error: {e}")
        errors.append(str(e))

    _log('windev_to_web', 'client', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


def sync_techniciens_incremental():
    """
    ÉTAPE 2b — Sync incrémentale T_Utilisateur (Technicien=1) → User + TechnicienProfile.

    Pour chaque technicien WinDev :
    1. Crée/met à jour un User Django (username=CodeUtilisateur ou tech_wd_{ID},
       password=tech_{IDUtilisateur}_temp à la première création uniquement).
    2. Crée/met à jour le TechnicienProfile associé.

    Doit s'exécuter APRÈS sync_clients pour que les techniciens puissent
    être assignés aux tickets qui référencent des pharmacies.
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []
    sc = _get_cursor('wd_technicien', 'windev_to_web')

    try:
        cursor = _windev_cursor()
        cursor.execute("""
            SELECT IDUtilisateur, CodeUtilisateur, NomComplet,
                   TelCel, telCel2, ActifOP, Disponible, IDProfil
            FROM T_Utilisateur
            WHERE Technicien = 1
              AND (IDUtilisateur > %s OR DateDernierModif >= %s)
            ORDER BY IDUtilisateur
        """, [sc.last_synced_id, sc.last_synced_at or '2000-01-01'])
        rows = cursor.fetchall()

        max_id = sc.last_synced_id
        for row in rows:
            try:
                (id_util, code, nom, tel, tel2, actif, disponible, profil) = row
                # --- Création/mise à jour du User Django technicien ---
                # Username : CodeUtilisateur WinDev ou tech_wd_{IDUtilisateur}
                username = code or f"tech_wd_{id_util}"

                user, created = User.objects.update_or_create(
                    windev_user_id=id_util,
                    defaults={
                        'username': username,
                        'role': 'technicien',
                        'first_name': (nom or '')[:150],
                        'phone': tel or '',
                        'phone2': tel2 or '',
                        'is_validated': True,
                        'is_active': bool(actif),
                    }
                )
                if created:
                    # Mot de passe temporaire — l'admin peut le changer via set_password
                    user.set_password(f"tech_{id_util}_temp")
                    user.save()

                # --- Création/mise à jour du profil technicien ---
                TechnicienProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'windev_technicien_id': id_util,
                        'is_available': bool(disponible) if disponible is not None else True,
                    }
                )
                synced += 1
                max_id = max(max_id, id_util)
            except Exception as e:
                failed += 1
                errors.append(f"Tech {row[0]}: {e}")

        sc.last_synced_id = max_id
        sc.last_synced_at = timezone.now()
        sc.save()

    except Exception as e:
        logger.error(f"sync_techniciens_incremental error: {e}")
        errors.append(str(e))

    _log('windev_to_web', 'technicien', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


# Mapping IDTypeIntervention WinDev → categorie Django
TYPE_INTERVENTION_MAP = {
    'DEPANNAGE': 'logiciel',
    'MIXTE': 'autre',
    'INVENTAIRE': 'autre',
    'MAINTENANCE': 'materiel',
    'MAJ': 'logiciel',
}


def sync_interventions_incremental():
    """
    ÉTAPE 2c — Sync incrémentale T_Intervention → Ticket.

    Dépend des étapes précédentes :
    - Les Pharmacies doivent exister (créées à l'étape 2a) pour lier le ticket.
    - Les Users techniciens doivent exister (créés à l'étape 2b) pour l'assignation.

    Chaque intervention WinDev devient un Ticket Django avec le statut
    déduit de EffectueOP/ValideOP.
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []
    sc = _get_cursor('wd_intervention', 'windev_to_web')

    try:
        cursor = _windev_cursor()
        # Colonnes réelles de T_Intervention (schema WinDev)
        cursor.execute("""
            SELECT i.IDIntervention, i.DateIntervention, i.IDClient,
                   i.IDTypeIntervention, i.IDUtilisateur,
                   i.IDIntervention2emeUtilisateur,
                   i.ValideOP, i.AnnuleOP, i.EffectueOP,
                   i.NbJours, i.DateChoisie, i.DateChoisieFin,
                   i.MontantTTC, i.Frais_Technicien,
                   i.DateAjout, i.DateDernierModif
            FROM T_Intervention i
            WHERE i.AnnuleOP = 0 AND i.IDIntervention > %s
            ORDER BY i.IDIntervention ASC
            LIMIT 200
        """, [sc.last_synced_id])
        rows = cursor.fetchall()

        # Charger la table T_TypeIntervention pour le libellé
        type_map = {}
        try:
            cursor.execute("SELECT IDTypeIntervention, LibTypeIntervention FROM T_TypeIntervention")
            for tid, tlib in cursor.fetchall():
                type_map[tid] = tlib or ''
        except Exception:
            pass

        max_id = sc.last_synced_id
        for row in rows:
            try:
                (id_inter, date_inter, id_client, id_type_inter,
                 id_user, id_user2, valide, annule, effectue,
                 nb_jours, date_choisie, date_choisie_fin,
                 montant_ttc, frais_tech,
                 date_ajout, date_modif) = row

                if Ticket.objects.filter(windev_intervention_id=id_inter).exists():
                    max_id = max(max_id, id_inter)
                    continue

                # --- Recherche de la pharmacie créée à l'étape 2a ---
                pharmacie = Pharmacie.objects.filter(windev_client_id=id_client).first()
                if not pharmacie:
                    max_id = max(max_id, id_inter)
                    continue

                # --- Recherche du technicien créé à l'étape 2b ---
                tech_user = User.objects.filter(windev_user_id=id_user).first() if id_user else None

                # Déterminer le type/catégorie depuis la table WinDev
                type_lib = type_map.get(id_type_inter, '') if id_type_inter else ''
                categorie = TYPE_INTERVENTION_MAP.get(type_lib.upper(), 'autre')

                # Déterminer le statut
                if effectue:
                    status = 'cloture'
                elif valide:
                    status = 'assigne'
                else:
                    status = 'nouveau'

                description = (
                    f"Intervention WinDev #{id_inter}\n"
                    f"Type: {type_lib}\n"
                    f"Nb jours: {nb_jours or 0}\n"
                    f"Montant TTC: {montant_ttc or 0} FCFA"
                )

                Ticket.objects.create(
                    objet=f"Intervention {type_lib} #{id_inter}",
                    type_intervention='sur_site',
                    categorie=categorie,
                    description=description,
                    urgence='moyen',
                    status=status,
                    pharmacie=pharmacie,
                    created_by=tech_user,
                    assigned_to=tech_user,
                    windev_intervention_id=id_inter,
                )
                synced += 1
                max_id = max(max_id, id_inter)
            except Exception as e:
                failed += 1
                errors.append(f"Intervention {row[0]}: {e}")

        sc.last_synced_id = max_id
        sc.last_synced_at = timezone.now()
        sc.save()

    except Exception as e:
        logger.error(f"sync_interventions_incremental error: {e}")
        errors.append(str(e))

    _log('windev_to_web', 'intervention', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


def sync_besoins_incremental():
    """
    ÉTAPE 2d — Sync incrémentale T_BesoinsClient → Ticket.
    Colonnes réelles : IDBesoinsClient, DateBesoin, DateAjout, HeureEnreg,
    DescriptionBesoin, ValideOP, Traite, Annule, NomTechnicien, IDClient,
    IDUtilisateur, IDUtilisateur_Validation, IDUtilisateur_Traitement,
    IDUtilisateur_Annulation, DateDernierModif.
    PAS de SourceBesoin/Priorite/StatutBesoin.
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []
    sc = _get_cursor('wd_besoin', 'windev_to_web')

    try:
        cursor = _windev_cursor()
        cursor.execute("""
            SELECT IDBesoinsClient, DateBesoin, DescriptionBesoin,
                   IDClient, NomTechnicien, ValideOP, Traite, Annule,
                   IDUtilisateur, DateAjout
            FROM T_BesoinsClient
            WHERE Annule = 0 AND IDBesoinsClient > %s
            ORDER BY IDBesoinsClient ASC
            LIMIT 200
        """, [sc.last_synced_id])
        rows = cursor.fetchall()

        max_id = sc.last_synced_id
        for row in rows:
            try:
                (id_besoin, date_besoin, description,
                 id_client, nom_tech, valide, traite, annule,
                 id_user, date_ajout) = row

                if Ticket.objects.filter(windev_besoin_id=id_besoin).exists():
                    max_id = max(max_id, id_besoin)
                    continue

                pharmacie = Pharmacie.objects.filter(windev_client_id=id_client).first()
                if not pharmacie:
                    max_id = max(max_id, id_besoin)
                    continue

                # Trouver le technicien par nom ou IDUtilisateur
                tech_user = None
                if id_user:
                    tech_user = User.objects.filter(windev_user_id=id_user).first()

                status = 'cloture' if traite else ('assigne' if valide else 'nouveau')
                Ticket.objects.create(
                    objet=f"Besoin client #{id_besoin}",
                    type_intervention='en_ligne',
                    categorie='logiciel',
                    description=description or f"Besoin importé (ID: {id_besoin})",
                    urgence='moyen',
                    status=status,
                    pharmacie=pharmacie,
                    assigned_to=tech_user,
                    windev_besoin_id=id_besoin,
                )
                synced += 1
                max_id = max(max_id, id_besoin)
            except Exception as e:
                failed += 1
                errors.append(f"Besoin {row[0]}: {e}")

        sc.last_synced_id = max_id
        sc.last_synced_at = timezone.now()
        sc.save()

    except Exception as e:
        logger.error(f"sync_besoins_incremental error: {e}")
        errors.append(str(e))

    _log('windev_to_web', 'besoin_client', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


def sync_localites_from_windev():
    """
    ÉTAPE 1 — Sync complète T_Ville + T_Localite → Region + Commune (référentiel).
    S'exécute EN PREMIER pour que les communes existent quand on sync les clients.
    T_Ville : IDVille (BIGINT PK), NomVille (VARCHAR 50 UNIQUE)
    T_Localite : IDLocalite (BIGINT PK), NomLocalite (VARCHAR 50), IDVille (FK)
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []

    try:
        cursor = _windev_cursor()
        cursor.execute("SELECT IDVille, NomVille FROM T_Ville ORDER BY NomVille")
        for row in cursor.fetchall():
            try:
                id_ville, nom = row
                Region.objects.update_or_create(
                    code=f"WD-{id_ville}",
                    defaults={'name': (nom or f'Ville #{id_ville}')[:100]}
                )
                synced += 1
            except Exception as e:
                failed += 1
                errors.append(f"Ville {row[0]}: {e}")

        cursor.execute("""
            SELECT l.IDLocalite, l.NomLocalite, l.IDVille
            FROM T_Localite l ORDER BY l.NomLocalite
        """)
        for row in cursor.fetchall():
            try:
                id_loc, nom, id_ville = row
                region = Region.objects.filter(code=f"WD-{id_ville}").first()
                if region:
                    Commune.objects.update_or_create(
                        code=f"WD-{id_loc}", region=region,
                        defaults={'name': (nom or f'Localité #{id_loc}')[:100]}
                    )
                    synced += 1
            except Exception as e:
                failed += 1
                errors.append(f"Localité {row[0]}: {e}")

    except Exception as e:
        logger.error(f"sync_localites error: {e}")
        errors.append(str(e))

    _log('windev_to_web', 'localite', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


# ═══════════════════════════════════════════════════════════
#  DJANGO → WINDEV  (écriture dans FacturationClient)
# ═══════════════════════════════════════════════════════════

def sync_pharmacies_to_windev():
    """
    ÉTAPE 3a — Sync Pharmacie → T_Client (Django → WinDev).
    - Pharmacies créées dans Django (sans windev_client_id) → INSERT dans T_Client.
    - Pharmacies déjà liées (windev_client_id existant) → UPDATE dans T_Client.
    Sens inverse : rend les pharmacies créées en ligne visibles dans WinDev.
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []
    sc = _get_cursor('dj_pharmacie_to_client', 'web_to_windev')

    try:
        # --- INSERT : pharmacies sans windev_client_id ---
        new_pharmacies = Pharmacie.objects.filter(
            windev_client_id__isnull=True,
        ).select_related('user', 'commune').order_by('id')

        cursor = _windev_write_cursor()

        for pharma in new_pharmacies:
            try:
                tel_fixe = pharma.tel_responsable or ''
                tel_cel = pharma.user.phone if pharma.user else ''
                tel_cel2 = pharma.user.phone2 if pharma.user else ''
                email = pharma.email_pharmacie or (pharma.user.email if pharma.user else '')

                # Trouver IDLocalite WinDev à partir de la commune Django
                id_localite = None
                if pharma.commune and pharma.commune.code and pharma.commune.code.startswith('WD-'):
                    try:
                        id_localite = int(pharma.commune.code.replace('WD-', ''))
                    except (ValueError, TypeError):
                        id_localite = None

                cursor.execute("""
                    INSERT INTO T_Client
                        (NomClient, TelFixe, TelCel, telCel2, Code_2ST,
                         AdresseGeo, EmailClient, NomResponsable, TelPharmacien,
                         SousContrat, IDLocalite, ActifOP, InterieurPays,
                         DateAjout, DateDernierModif)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s, NOW(), NOW())
                """, [
                    (pharma.nom_pharmacie or '')[:100],
                    tel_fixe[:30],
                    tel_cel[:30],
                    tel_cel2[:20],
                    (pharma.code_2st or '')[:10],
                    (pharma.adresse or '')[:50],
                    email[:50],
                    (pharma.nom_responsable or '')[:50],
                    (pharma.tel_responsable or '')[:15],
                    1 if pharma.sous_contrat else 0,
                    id_localite,
                    1 if pharma.interieur_pays else 0,
                ])

                client_id = cursor.lastrowid
                if client_id:
                    pharma.windev_client_id = client_id
                    pharma.save(update_fields=['windev_client_id', 'updated_at'])

                synced += 1
            except Exception as e:
                failed += 1
                errors.append(f"Pharmacie INSERT {pharma.id} ({pharma.nom_pharmacie}): {e}")

        # --- UPDATE : pharmacies déjà liées et modifiées depuis le dernier sync ---
        if sc.last_synced_at:
            updated_pharmacies = Pharmacie.objects.filter(
                windev_client_id__isnull=False,
                updated_at__gte=sc.last_synced_at,
            ).select_related('user', 'commune').order_by('id')

            for pharma in updated_pharmacies:
                try:
                    tel_fixe = pharma.tel_responsable or ''
                    tel_cel = pharma.user.phone if pharma.user else ''
                    tel_cel2 = pharma.user.phone2 if pharma.user else ''
                    email = pharma.email_pharmacie or (pharma.user.email if pharma.user else '')

                    id_localite = None
                    if pharma.commune and pharma.commune.code and pharma.commune.code.startswith('WD-'):
                        try:
                            id_localite = int(pharma.commune.code.replace('WD-', ''))
                        except (ValueError, TypeError):
                            id_localite = None

                    cursor.execute("""
                        UPDATE T_Client
                        SET NomClient = %s, TelFixe = %s, TelCel = %s, telCel2 = %s,
                            Code_2ST = %s, AdresseGeo = %s, EmailClient = %s,
                            NomResponsable = %s, TelPharmacien = %s,
                            SousContrat = %s, IDLocalite = %s,
                            InterieurPays = %s, DateDernierModif = NOW()
                        WHERE IDClient = %s
                    """, [
                        (pharma.nom_pharmacie or '')[:100],
                        tel_fixe[:30],
                        tel_cel[:30],
                        tel_cel2[:20],
                        (pharma.code_2st or '')[:10],
                        (pharma.adresse or '')[:50],
                        email[:50],
                        (pharma.nom_responsable or '')[:50],
                        (pharma.tel_responsable or '')[:15],
                        1 if pharma.sous_contrat else 0,
                        id_localite,
                        1 if pharma.interieur_pays else 0,
                        pharma.windev_client_id,
                    ])
                    synced += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"Pharmacie UPDATE {pharma.id} ({pharma.nom_pharmacie}): {e}")

        sc.last_synced_at = timezone.now()
        sc.save()

    except Exception as e:
        logger.error(f"sync_pharmacies_to_windev error: {e}")
        errors.append(str(e))

    _log('web_to_windev', 'pharmacie_to_client', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


def sync_tickets_to_windev():
    """
    ÉTAPE 3b — Sync Ticket → T_BesoinsClient (Django → WinDev).
    Colonnes réelles T_BesoinsClient : IDBesoinsClient, DateBesoin, DateAjout,
    HeureEnreg, DescriptionBesoin, ValideOP, Traite, Annule, NomTechnicien,
    IDClient, IDUtilisateur, IDUtilisateur_Validation, IDUtilisateur_Traitement,
    IDUtilisateur_Annulation, DateDernierModif.
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []
    sc = _get_cursor('dj_ticket_to_besoin', 'web_to_windev')

    try:
        tickets = Ticket.objects.filter(
            windev_besoin_id__isnull=True,
            windev_intervention_id__isnull=True,
            id__gt=sc.last_synced_id,
        ).select_related('pharmacie', 'assigned_to').order_by('id')[:200]

        cursor = _windev_write_cursor()
        max_id = sc.last_synced_id

        for ticket in tickets:
            try:
                id_client = 0
                if ticket.pharmacie and ticket.pharmacie.windev_client_id:
                    id_client = ticket.pharmacie.windev_client_id

                id_user = 0
                if ticket.assigned_to and ticket.assigned_to.windev_user_id:
                    id_user = ticket.assigned_to.windev_user_id

                tech_name = ''
                if ticket.assigned_to:
                    tech_name = ticket.assigned_to.get_full_name()[:50]

                valide = 1 if ticket.status in ('assigne', 'en_cours', 'resolu', 'cloture') else 0
                traite = 1 if ticket.status in ('resolu', 'cloture') else 0

                cursor.execute("""
                    INSERT INTO T_BesoinsClient
                        (DateBesoin, DescriptionBesoin, IDClient,
                         NomTechnicien, ValideOP, Traite, Annule,
                         IDUtilisateur, DateAjout, DateDernierModif)
                    VALUES (%s, %s, %s, %s, %s, %s, 0, %s, NOW(), NOW())
                """, [
                    ticket.created_at.date() if ticket.created_at else timezone.now().date(),
                    f"[SAV Web] {ticket.objet}\n\n{ticket.description}"[:65535],
                    id_client,
                    tech_name,
                    valide,
                    traite,
                    id_user,
                ])

                besoin_id = cursor.lastrowid
                if besoin_id:
                    ticket.windev_besoin_id = besoin_id
                    ticket.save(update_fields=['windev_besoin_id', 'updated_at'])

                synced += 1
                max_id = max(max_id, ticket.id)
            except Exception as e:
                failed += 1
                errors.append(f"Ticket {ticket.reference}: {e}")

        sc.last_synced_id = max_id
        sc.last_synced_at = timezone.now()
        sc.save()

    except Exception as e:
        logger.error(f"sync_tickets_to_windev error: {e}")
        errors.append(str(e))

    _log('web_to_windev', 'ticket_to_besoin', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


def sync_rapports_to_windev():
    """
    ÉTAPE 3c — Sync RapportIntervention → T_DetailIntervention (Django → WinDev).
    Colonnes réelles T_DetailIntervention : IDDetailIntervention,
    IDIntervention (FK), IDNature (FK T_Nature), DescriptionDetail (LONGTEXT),
    IDUtilisateur, DateAjout, DateDernierModif.
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []
    sc = _get_cursor('dj_rapport_to_detail', 'web_to_windev')

    try:
        rapports = RapportIntervention.objects.filter(
            windev_detail_intervention_id__isnull=True,
            id__gt=sc.last_synced_id,
        ).select_related('ticket', 'ticket__pharmacie', 'technicien').order_by('id')[:200]

        cursor = _windev_write_cursor()
        max_id = sc.last_synced_id

        for rapport in rapports:
            try:
                ticket = rapport.ticket
                windev_inter_id = ticket.windev_intervention_id
                if not windev_inter_id:
                    max_id = max(max_id, rapport.id)
                    continue

                # Mapper la catégorie Django vers IDNature WinDev (T_Nature)
                # Par défaut 0, sera ignoré si la FK n'existe pas
                id_nature = 0

                id_user = 0
                if rapport.technicien and rapport.technicien.windev_user_id:
                    id_user = rapport.technicien.windev_user_id

                resultat_txt = rapport.get_resultat_display() if rapport.resultat else ''
                # Colonne réelle : DescriptionDetail (LONGTEXT)
                description_detail = (
                    f"[SAV Web] {rapport.actions_realisees}\n"
                    f"Résultat: {resultat_txt}\n"
                    f"Temps: {rapport.temps_passe_minutes} min\n"
                    f"Recommandations: {rapport.recommandations or 'N/A'}"
                )

                cursor.execute("""
                    INSERT INTO T_DetailIntervention
                        (IDIntervention, IDNature, DescriptionDetail,
                         IDUtilisateur, DateAjout, DateDernierModif)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                """, [
                    windev_inter_id,
                    id_nature,
                    description_detail[:65535],
                    id_user,
                ])

                detail_id = cursor.lastrowid
                if detail_id:
                    rapport.windev_detail_intervention_id = detail_id
                    rapport.save(update_fields=['windev_detail_intervention_id', 'updated_at'])

                synced += 1
                max_id = max(max_id, rapport.id)
            except Exception as e:
                failed += 1
                errors.append(f"Rapport {rapport.id}: {e}")

        sc.last_synced_id = max_id
        sc.last_synced_at = timezone.now()
        sc.save()

    except Exception as e:
        logger.error(f"sync_rapports_to_windev error: {e}")
        errors.append(str(e))

    _log('web_to_windev', 'rapport_to_detail', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


def sync_ticket_status_to_windev():
    """
    ÉTAPE 3d — Met à jour le statut des besoins WinDev quand un ticket Django
    est résolu/clôturé. Mise à jour des champs Traite et ValideOP dans T_BesoinsClient.
    """
    started = timezone.now()
    synced, failed, errors = 0, 0, []
    sc = _get_cursor('dj_ticket_status_update', 'web_to_windev')

    try:
        # Tickets qui viennent de WinDev ET ont changé de statut
        tickets = Ticket.objects.filter(
            windev_besoin_id__isnull=False,
            updated_at__gte=sc.last_synced_at or timezone.make_aware(dt.datetime(2000, 1, 1)),
        ).exclude(
            status='nouveau'
        ).order_by('id')[:200]

        cursor = _windev_write_cursor()

        for ticket in tickets:
            try:
                valide = 1 if ticket.status in ('assigne', 'en_cours', 'resolu', 'cloture') else 0
                traite = 1 if ticket.status in ('resolu', 'cloture') else 0
                annule = 0

                tech_name = ''
                if ticket.assigned_to:
                    tech_name = ticket.assigned_to.get_full_name()[:50]

                cursor.execute("""
                    UPDATE T_BesoinsClient
                    SET ValideOP = %s, Traite = %s, Annule = %s,
                        NomTechnicien = %s, DateDernierModif = NOW()
                    WHERE IDBesoinsClient = %s
                """, [valide, traite, annule, tech_name, ticket.windev_besoin_id])

                synced += 1
            except Exception as e:
                failed += 1
                errors.append(f"Ticket status {ticket.reference}: {e}")

        sc.last_synced_at = timezone.now()
        sc.save()

    except Exception as e:
        logger.error(f"sync_ticket_status_to_windev error: {e}")
        errors.append(str(e))

    _log('web_to_windev', 'ticket_status_update', synced, failed, errors, started)
    return {'synced': synced, 'failed': failed}


# ═══════════════════════════════════════════════════════════
#  FONCTIONS AGRÉGÉES (appelées par les tâches Celery)
# ═══════════════════════════════════════════════════════════

def run_windev_to_django_incremental():
    """
    Sync incrémentale WinDev → Django (rapide, toutes les 2 min).
    Ordre : clients (→ users pharmacie) → techniciens (→ users tech) → tickets.
    L'ordre est IMPORTANT : les tickets dépendent des users/pharmacies créés avant.
    """
    results = {}
    results['clients'] = sync_clients_incremental()
    results['techniciens'] = sync_techniciens_incremental()
    results['interventions'] = sync_interventions_incremental()
    results['besoins'] = sync_besoins_incremental()
    return results


def run_django_to_windev_incremental():
    """
    Sync incrémentale Django → WinDev (rapide, toutes les 2 min).
    Exporte les données créées dans le portail web vers la base WinDev.
    """
    results = {}
    results['pharmacies_to_client'] = sync_pharmacies_to_windev()
    results['tickets_to_besoin'] = sync_tickets_to_windev()
    results['rapports_to_detail'] = sync_rapports_to_windev()
    results['ticket_status'] = sync_ticket_status_to_windev()
    return results


def run_windev_referentials():
    """
    Sync référentiels (localités) — ÉTAPE 1.
    S'exécute en premier pour que les communes/régions existent
    avant la sync des clients (qui référencent des communes).
    """
    results = {}
    results['localites'] = sync_localites_from_windev()
    return results


def run_full_sync():
    """
    Synchronisation complète bidirectionnelle.
    Ordre d'exécution :
      1. Référentiels (villes/localités) → Region/Commune
      2. WinDev → Django (clients → users pharmacie, techniciens → users tech, interventions/besoins → tickets)
      3. Django → WinDev (pharmacies → T_Client, tickets → T_BesoinsClient, rapports → T_DetailIntervention)
    """
    results = {}
    results['referentials'] = run_windev_referentials()
    results['windev_to_django'] = run_windev_to_django_incremental()
    results['django_to_windev'] = run_django_to_windev_incremental()
    return results
