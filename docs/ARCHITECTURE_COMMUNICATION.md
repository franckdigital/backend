# Architecture de communication entre Django (VPS) et WinDev (Serveur local)

## 1. Vue d'ensemble

```
┌─────────────────────────────┐              ┌──────────────────────────────────┐
│       VPS DJANGO            │              │       SERVEUR WINDEV             │
│   (Application Web SAV)     │              │   (Application Desktop)          │
│                             │              │                                  │
│   - API REST (DRF)         │              │   - App WinDev (desktop)         │
│   - React Admin (front)    │              │   - MySQL Server                 │
│   - React Native (mobile)  │              │                                  │
│                             │              │   Bases de données :             │
│   Pas de MySQL local        │              │   ┌──────────────────────────┐   │
│   Se connecte au MySQL      │◄────────────►│   │ FacturationClient       │   │
│   distant via réseau        │  TCP 3306    │   │ (base WinDev existante) │   │
│                             │  (MySQL)     │   ├──────────────────────────┤   │
│                             │              │   │ sav_pharmacie           │   │
│                             │              │   │ (base Django)           │   │
│                             │              │   └──────────────────────────┘   │
└─────────────────────────────┘              └──────────────────────────────────┘
```

---

## 2. Les deux bases de données

### Base `FacturationClient` (WinDev)
- **Gérée par** : l'application WinDev desktop
- **Contenu** : clients (pharmacies), utilisateurs/techniciens, interventions, besoins clients, factures, produits, stock, etc.
- **Accès Django** : **SELECT sur toutes les tables** + **INSERT/UPDATE sur T_BesoinsClient et T_DetailIntervention**
- **Utilisateur MySQL** : `sav_sync` (droits limités par table)

### Base `sav_pharmacie` (Django)
- **Gérée par** : l'application web Django
- **Contenu** : tickets SAV, rapports d'intervention, zones géographiques, messages, notifications, évaluations, etc.
- **Accès Django** : **LECTURE + ÉCRITURE** complète
- **Utilisateur MySQL** : `sav_app`

---

## 3. Comment Django lit les données WinDev

### Mécanisme : Raw SQL via curseur dédié

Django ne crée PAS de modèles ORM pour les tables WinDev. Il utilise des **requêtes SQL brutes** via un curseur sur la connexion `windev` :

```python
# Dans apps/windev_sync/services.py
from django.db import connections

def _windev_cursor():
    return connections['windev'].cursor()

# Exemple : lire les clients WinDev
cursor = _windev_cursor()
cursor.execute("""
    SELECT IDClient, NomClient, TelFixe, TelCel, Code_2ST,
           AdresseGeo, EmailClient, NomResponsable
    FROM T_Client
    WHERE ActifOP = 1
""")
rows = cursor.fetchall()
```

### Pourquoi du raw SQL et pas l'ORM ?
- Les tables WinDev ont des noms et structures non-standard (noms en français, types WinDev)
- On ne veut PAS que Django crée/modifie les tables WinDev (`migrate` est bloqué par le router)
- Le raw SQL permet de lire exactement ce qu'on veut sans interférer

---

## 4. Synchronisation des données

### Synchronisation BIDIRECTIONNELLE automatique (implémentée)

La synchronisation est **bidirectionnelle** et **automatique** via **Celery Beat** :
- **Toutes les 2 minutes** : sync incrémentale dans les deux sens
- **Toutes les 15 minutes** : sync des référentiels (villes, localités)

Délai max de visibilité : **2 minutes**.

### Flux de synchronisation

```
  ┌─────────────────────────┐                    ┌─────────────────────────┐
  │   sav_pharmacie (Django) │                    │  FacturationClient (WD) │
  │                          │                    │                         │
  │  WinDev → Django         │                    │  Django → WinDev        │
  │  (toutes les 2 min)      │                    │  (toutes les 2 min)     │
  │                          │                    │                         │
  │  T_Client ──────► Pharma │                    │  Ticket ──────► T_Besoi │
  │  T_Utilisat ────► User   │                    │  Rapport ─────► T_Detai │
  │  T_Interven ────► Ticket │                    │  Statut ──────► UPDATE  │
  │  T_BesoinsC ────► Ticket │                    │   T_BesoinsClient       │
  │  T_Ville ───────► Region │                    │                         │
  │  T_Localite ────► Commun │                    │                         │
  └─────────────────────────┘                    └─────────────────────────┘
```

### Mécanisme : Celery Beat + sync incrémentale

```python
# config/settings.py — Planning Celery Beat
CELERY_BEAT_SCHEDULE = {
    # WinDev → Django (toutes les 2 min)
    'sync-windev-to-django-fast': {
        'task': 'apps.windev_sync.tasks.sync_windev_to_django_incremental',
        'schedule': 120.0,
    },
    # Django → WinDev (toutes les 2 min)
    'sync-django-to-windev-fast': {
        'task': 'apps.windev_sync.tasks.sync_django_to_windev_incremental',
        'schedule': 120.0,
    },
    # Référentiels (toutes les 15 min)
    'sync-windev-referentials': {
        'task': 'apps.windev_sync.tasks.sync_windev_referentials',
        'schedule': 900.0,
    },
}
```

La sync est **incrémentale** grâce au modèle `SyncCursor` qui stocke le dernier ID/date synchronisé pour chaque entité. Seuls les enregistrements nouveaux ou modifiés sont traités à chaque cycle.

### Déclenchement manuel (API)

```
POST /api/v1/windev/sync/windev-to-django/   → WinDev → Django
POST /api/v1/windev/sync/django-to-windev/   → Django → WinDev
POST /api/v1/windev/sync/full/               → Bidirectionnel complet
GET  /api/v1/windev/status/                  → État de la sync
```

Chaque endpoint accepte `{"mode": "sync"}` pour exécution synchrone ou `{"mode": "async"}` (défaut) pour lancer en arrière-plan via Celery.

### Commande management

```bash
python manage.py sync_windev                   # Sync complète bidirectionnelle
python manage.py sync_windev --windev-to-django # WinDev → Django seulement
python manage.py sync_windev --django-to-windev # Django → WinDev seulement
python manage.py sync_windev --referentials     # Référentiels uniquement
python manage.py sync_windev --reset-cursors    # Reset curseurs (force re-sync)
```

---

## 5. Ce qui est visible et ce qui ne l'est pas

### Données WinDev → Django (automatique, toutes les 2 min)

| Action dans WinDev | Visible côté Django ? | Délai |
|---|---|---|
| Nouveau client (pharmacie) | ✅ Oui | ≤ 2 min |
| Modification client | ✅ Oui | ≤ 2 min |
| Nouveau technicien | ✅ Oui | ≤ 2 min |
| Nouvelle intervention | ✅ Oui | ≤ 2 min |
| Nouveau besoin client | ✅ Oui | ≤ 2 min |
| Factures / Ventes | ❌ Non (pas synchronisé) | — |
| Stock / Produits | ❌ Non (pas synchronisé) | — |
| Commandes fournisseurs | ❌ Non (pas synchronisé) | — |

### Données Django → WinDev (automatique, toutes les 2 min)

| Action dans Django | Visible côté WinDev ? | Délai |
|---|---|---|
| Nouveau ticket SAV | ✅ Oui → T_BesoinsClient | ≤ 2 min |
| Ticket résolu/clôturé | ✅ Oui → UPDATE T_BesoinsClient | ≤ 2 min |
| Rapport d'intervention | ✅ Oui → T_DetailIntervention | ≤ 2 min |
| Assignation technicien | ✅ Oui → UPDATE NomTechnicien | ≤ 2 min |
| Message sur ticket | ❌ Non (données propres à Django) | — |
| Notification | ❌ Non (données propres à Django) | — |
| Évaluation pharmacie | ❌ Non (données propres à Django) | — |

> **Note** : Pour rendre les données Django visibles dans WinDev, il faudrait que WinDev lise la base `sav_pharmacie` ou appelle l'API Django. C'est possible mais nécessite un développement côté WinDev.

---

## 6. Détail du processus de synchronisation

### Étape par étape : sync des clients

```
1. Django se connecte à FacturationClient (connexion 'windev')
2. Exécute : SELECT * FROM T_Client WHERE ActifOP = 1
3. Pour chaque client WinDev :
   a. Cherche si un Pharmacie avec windev_client_id = IDClient existe
   b. Si NON → Crée un User (rôle pharmacie) + Pharmacie
   c. Si OUI → Met à jour les infos (nom, tel, adresse...)
4. Enregistre un log dans SyncLog (nb synchro, nb erreurs)
```

### Correspondances des tables

```
WinDev (FacturationClient)     →     Django (sav_pharmacie)
─────────────────────────────────────────────────────────────
T_Client                       →     User (role=pharmacie) + Pharmacie
  IDClient                     →     Pharmacie.windev_client_id
  NomClient                    →     Pharmacie.nom_pharmacie
  TelFixe, TelCel              →     User.phone
  Code_2ST                     →     Pharmacie.code_2st
  AdresseGeo                   →     Pharmacie.adresse
  NomResponsable               →     Pharmacie.nom_responsable
  SousContrat                  →     Pharmacie.sous_contrat

T_Utilisateur (Technicien=1)   →     User (role=technicien) + TechnicienProfile
  IDUtilisateur                →     User.windev_user_id
  CodeUtilisateur              →     User.username
  NomComplet                   →     User.first_name
  TelCel                       →     User.phone

T_Intervention                 →     Ticket
  IDIntervention               →     Ticket.windev_intervention_id
  IDClient                     →     Ticket.pharmacie (via windev_client_id)
  IDUtilisateur                →     Ticket.assigned_to (via windev_user_id)

T_BesoinsClient                →     Ticket
  IDBesoinsClient              →     Ticket.windev_besoin_id
  DescriptionBesoin            →     Ticket.description
  IDClient                     →     Ticket.pharmacie

T_Ville                        →     Region
T_Localite                     →     Commune
```

---

## 7. Sécurité de la communication

### Connexion MySQL distante

```
VPS Django ────── TCP 3306 ──────► MySQL (serveur WinDev)
   │                                      │
   │  Utilisateur : sav_app               │ Accès : sav_pharmacie (ALL)
   │  Utilisateur : sav_readonly          │ Accès : FacturationClient (SELECT)
   │                                      │
   │  Authentification par IP + password  │
   └──────────────────────────────────────┘
```

### Mesures de sécurité

1. **Firewall** : port 3306 ouvert uniquement pour l'IP du VPS Django
2. **Utilisateurs MySQL restreints par IP** : `'sav_app'@'IP_DU_VPS'`
3. **Lecture seule sur WinDev** : `sav_readonly` n'a que `SELECT`
4. **Pas de migration Django sur la base WinDev** : bloqué par `WindevRouter`
5. **Recommandé** : tunnel VPN (WireGuard) entre les 2 serveurs pour chiffrer le trafic

### Configuration firewall (serveur WinDev)

```bash
# Windows (PowerShell admin)
netsh advfirewall firewall add rule name="MySQL VPS SAV" `
    dir=in action=allow protocol=TCP localport=3306 `
    remoteip=IP_DU_VPS

# Linux (ufw)
sudo ufw allow from IP_DU_VPS to any port 3306
```

### Configuration MySQL (serveur WinDev)

```ini
# my.cnf ou my.ini
[mysqld]
bind-address = 0.0.0.0    # Accepter les connexions distantes
# OU pour plus de sécurité :
# bind-address = IP_LOCALE_DU_SERVEUR
```

---

## 8. Mise en place étape par étape

### Sur le serveur WinDev (MySQL)

```bash
# 1. Exécuter le script SQL
mysql -u root -p < sql_setup_windev_server.sql

# 2. Modifier my.cnf
# Ajouter : bind-address = 0.0.0.0

# 3. Redémarrer MySQL
# Windows : net stop mysql && net start mysql
# Linux   : sudo systemctl restart mysql

# 4. Ouvrir le firewall pour l'IP du VPS
```

### Sur le VPS Django

```bash
# 1. Configurer .env
DB_HOST=IP_SERVEUR_WINDEV
DB_USER=sav_app
DB_PASSWORD=mot_de_passe_fort
WINDEV_DB_HOST=IP_SERVEUR_WINDEV
WINDEV_DB_USER=sav_readonly
WINDEV_DB_PASSWORD=mot_de_passe_readonly

# 2. Tester la connexion
python manage.py dbshell
# Si ça se connecte → tout est bon

# 3. Lancer les migrations
python manage.py migrate

# 4. Créer le superutilisateur
python manage.py createsuperuser

# 5. Première synchronisation
# Via l'API : POST /api/v1/windev/sync/full/
# Ou : python manage.py shell -c "from apps.windev_sync.services import run_full_sync; print(run_full_sync())"

# 6. Configurer le cron pour la sync automatique
crontab -e
# Ajouter :
# */15 * * * * cd /path/to/backend && /path/to/venv/bin/python manage.py sync_windev >> /var/log/sav_sync.log 2>&1
```

---

## 9. Résumé

| Question | Réponse |
|---|---|
| Les 2 apps utilisent le même MySQL ? | ✅ Oui, le MySQL du serveur WinDev |
| Django peut lire les données WinDev ? | ✅ Oui (SELECT sur toutes les tables) |
| Django peut écrire dans la base WinDev ? | ✅ Oui, sur T_BesoinsClient et T_DetailIntervention uniquement (user `sav_sync`) |
| WinDev peut lire les données Django ? | ✅ Oui, via T_BesoinsClient et T_DetailIntervention (données Django préfixées [SAV Web]) |
| Les changements WinDev sont visibles côté Django ? | ✅ Oui, délai ≤ 2 min (sync Celery Beat automatique) |
| Les changements Django sont visibles côté WinDev ? | ✅ Oui, délai ≤ 2 min (tickets → T_BesoinsClient, rapports → T_DetailIntervention) |
| La communication est sécurisée ? | ✅ Firewall + IP restreinte + users dédiés par table |
| Risque de corrompre les données WinDev ? | ❌ Minimal (Django écrit uniquement dans 2 tables, INSERT/UPDATE seulement, préfixé [SAV Web]) |
