"""
Migration autonome : création des tables de synchronisation MySQL
dans la base WinDev (FacturationClient).

Ces tables sont partagées entre WinDev et Django.
- Django les utilise via raw SQL (connections['windev'])
- WinDev les utilise via accès natif MySQL

La migration utilise RunPython pour contourner le router qui bloque
les migrations sur la base 'windev'. Elle exécute les CREATE TABLE
IF NOT EXISTS pour ne pas casser une base existante.

Tables créées :
  - T_Ville (référentiel villes)
  - T_Localite (référentiel localités, FK → T_Ville)
  - T_Client (pharmacies/clients)
  - T_Profil (profils utilisateurs)
  - T_Utilisateur (techniciens/utilisateurs)
  - T_TypeIntervention (référentiel types d'intervention)
  - T_Nature (référentiel natures d'intervention)
  - T_Intervention (interventions planifiées)
  - T_BesoinsClient (besoins/tickets SAV — table de sync bidirectionnelle)
  - T_DetailIntervention (détails d'intervention — table de sync bidirectionnelle)
"""

from django.db import migrations


# ─────────────────────────────────────────────────────────────
#  SQL de création des tables WinDev (CREATE TABLE IF NOT EXISTS)
# ─────────────────────────────────────────────────────────────

FORWARD_SQL = """

-- ============================================================
-- RÉFÉRENTIELS
-- ============================================================

CREATE TABLE IF NOT EXISTS T_Ville (
    IDVille       BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    NomVille      VARCHAR(50) DEFAULT NULL,
    DateAjout     TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_nom_ville (NomVille)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS T_Localite (
    IDLocalite    BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    NomLocalite   VARCHAR(50) DEFAULT NULL,
    IDVille       BIGINT DEFAULT NULL,
    DateAjout     TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_localite_ville (IDVille),
    CONSTRAINT fk_localite_ville FOREIGN KEY (IDVille)
        REFERENCES T_Ville (IDVille) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS T_Profil (
    IDProfil      VARCHAR(20) NOT NULL PRIMARY KEY,
    LibProfil     VARCHAR(50) DEFAULT NULL,
    DateAjout     TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS T_TypeIntervention (
    IDTypeIntervention  VARCHAR(20) NOT NULL PRIMARY KEY,
    LibTypeIntervention VARCHAR(50) DEFAULT NULL,
    DateAjout           TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS T_Nature (
    IDNature      BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    LibNature     VARCHAR(100) DEFAULT NULL,
    DateAjout     TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- TABLES MÉTIER (lues par Django, gérées par WinDev)
-- ============================================================

CREATE TABLE IF NOT EXISTS T_Client (
    IDClient          BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    NomClient         VARCHAR(100) DEFAULT NULL,
    TelFixe           VARCHAR(30) DEFAULT NULL,
    TelCel            VARCHAR(30) DEFAULT NULL,
    telCel2           VARCHAR(20) DEFAULT NULL,
    Code_2ST          VARCHAR(10) DEFAULT NULL,
    AdresseGeo        VARCHAR(50) DEFAULT NULL,
    EmailClient       VARCHAR(50) DEFAULT NULL,
    NomResponsable    VARCHAR(50) DEFAULT NULL,
    TelPharmacien     VARCHAR(15) DEFAULT NULL,
    SousContrat       TINYINT NOT NULL DEFAULT 0,
    IDLocalite        BIGINT DEFAULT NULL,
    ActifOP           TINYINT NOT NULL DEFAULT 1,
    InterieurPays     TINYINT NOT NULL DEFAULT 0,
    DateMaintenance   DATE DEFAULT NULL,
    MontantContrat    INTEGER DEFAULT 0,
    MontantInventaire INTEGER DEFAULT 0,
    Solde             INTEGER DEFAULT 0,
    ClientHorsM       TINYINT NOT NULL DEFAULT 0,
    DateAjout         TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_client_actif (ActifOP),
    INDEX idx_client_date_modif (DateDernierModif),
    INDEX idx_client_code_2st (Code_2ST),
    INDEX idx_client_localite (IDLocalite),
    CONSTRAINT fk_client_localite FOREIGN KEY (IDLocalite)
        REFERENCES T_Localite (IDLocalite) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS T_Utilisateur (
    IDUtilisateur     BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    CodeUtilisateur   VARCHAR(20) DEFAULT NULL,
    NomComplet        VARCHAR(50) DEFAULT NULL,
    MotDePasse        VARCHAR(100) DEFAULT NULL,
    TelCel            VARCHAR(30) DEFAULT NULL,
    telCel2           VARCHAR(20) DEFAULT NULL,
    ActifOP           TINYINT NOT NULL DEFAULT 1,
    Technicien        TINYINT NOT NULL DEFAULT 0,
    Disponible        TINYINT NOT NULL DEFAULT 1,
    IDProfil          VARCHAR(20) DEFAULT NULL,
    DateAjout         TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_utilisateur (CodeUtilisateur),
    INDEX idx_utilisateur_tech_actif (Technicien, ActifOP),
    INDEX idx_utilisateur_date_modif (DateDernierModif),
    INDEX idx_utilisateur_profil (IDProfil),
    CONSTRAINT fk_utilisateur_profil FOREIGN KEY (IDProfil)
        REFERENCES T_Profil (IDProfil) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS T_Intervention (
    IDIntervention    BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    DateIntervention  DATE DEFAULT NULL,
    IDClient          BIGINT DEFAULT NULL,
    IDTypeIntervention VARCHAR(20) DEFAULT NULL,
    IDUtilisateur     BIGINT DEFAULT NULL,
    IDIntervention2emeUtilisateur BIGINT DEFAULT NULL,
    ValideOP          TINYINT NOT NULL DEFAULT 0,
    AnnuleOP          TINYINT NOT NULL DEFAULT 0,
    EffectueOP        TINYINT NOT NULL DEFAULT 0,
    NbJours           INTEGER DEFAULT 0,
    DatePlanifie1     DATE DEFAULT NULL,
    DatePlanifie1_Fin DATE DEFAULT NULL,
    DatePlanifie2     DATE DEFAULT NULL,
    DateChoisie       DATE DEFAULT NULL,
    DateChoisieFin    DATE DEFAULT NULL,
    MontantTTC        INTEGER DEFAULT 0,
    Frais_Technicien  INTEGER DEFAULT 0,
    IDUtilisateur_Saisie BIGINT DEFAULT NULL,
    DateAjout         TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_intervention_annule (AnnuleOP),
    INDEX idx_intervention_client (IDClient),
    INDEX idx_intervention_utilisateur (IDUtilisateur),
    INDEX idx_intervention_type (IDTypeIntervention),
    INDEX idx_intervention_date_modif (DateDernierModif),
    CONSTRAINT fk_intervention_client FOREIGN KEY (IDClient)
        REFERENCES T_Client (IDClient) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_intervention_utilisateur FOREIGN KEY (IDUtilisateur)
        REFERENCES T_Utilisateur (IDUtilisateur) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_intervention_type FOREIGN KEY (IDTypeIntervention)
        REFERENCES T_TypeIntervention (IDTypeIntervention) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- TABLES DE SYNCHRONISATION BIDIRECTIONNELLE
-- (Django INSERT + UPDATE, WinDev INSERT + UPDATE)
-- ============================================================

CREATE TABLE IF NOT EXISTS T_BesoinsClient (
    IDBesoinsClient   BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    DateBesoin        DATE DEFAULT NULL,
    DateAjout         TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    HeureEnreg        TIME DEFAULT NULL,
    DescriptionBesoin LONGTEXT,
    ValideOP          TINYINT NOT NULL DEFAULT 0,
    Traite            TINYINT NOT NULL DEFAULT 0,
    Annule            TINYINT NOT NULL DEFAULT 0,
    NomTechnicien     VARCHAR(50) DEFAULT NULL,
    IDClient          BIGINT DEFAULT NULL,
    IDUtilisateur     INTEGER DEFAULT 0,
    IDUtilisateur_Validation  INTEGER DEFAULT 0,
    IDUtilisateur_Traitement  INTEGER DEFAULT 0,
    IDUtilisateur_Annulation  INTEGER DEFAULT 0,
    DateDernierModif  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_besoin_client (IDClient),
    INDEX idx_besoin_annule (Annule),
    INDEX idx_besoin_traite (Traite),
    INDEX idx_besoin_valide (ValideOP),
    INDEX idx_besoin_date_modif (DateDernierModif),
    CONSTRAINT fk_besoin_client FOREIGN KEY (IDClient)
        REFERENCES T_Client (IDClient) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS T_DetailIntervention (
    IDDetailIntervention BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    IDIntervention    BIGINT DEFAULT NULL,
    IDNature          BIGINT DEFAULT NULL,
    DescriptionDetail LONGTEXT,
    IDUtilisateur     BIGINT DEFAULT 0,
    DateAjout         TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_detail_intervention (IDIntervention),
    INDEX idx_detail_nature (IDNature),
    INDEX idx_detail_utilisateur (IDUtilisateur),
    CONSTRAINT fk_detail_intervention FOREIGN KEY (IDIntervention)
        REFERENCES T_Intervention (IDIntervention) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_detail_nature FOREIGN KEY (IDNature)
        REFERENCES T_Nature (IDNature) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- DONNÉES DE RÉFÉRENCE INITIALES
-- ============================================================

INSERT IGNORE INTO T_TypeIntervention (IDTypeIntervention, LibTypeIntervention) VALUES
    ('DEPANNAGE', 'Dépannage'),
    ('MIXTE', 'Mixte'),
    ('INVENTAIRE', 'Inventaire'),
    ('MAINTENANCE', 'Maintenance'),
    ('MAJ', 'Mise à jour');

INSERT IGNORE INTO T_Profil (IDProfil, LibProfil) VALUES
    ('ADMIN', 'Administrateur'),
    ('TECH', 'Technicien'),
    ('SAISIE', 'Saisie');

"""

# SQL de rollback (supprime les tables dans l'ordre inverse des FK)
REVERSE_SQL = """
DROP TABLE IF EXISTS T_DetailIntervention;
DROP TABLE IF EXISTS T_BesoinsClient;
DROP TABLE IF EXISTS T_Intervention;
DROP TABLE IF EXISTS T_Utilisateur;
DROP TABLE IF EXISTS T_Client;
DROP TABLE IF EXISTS T_Nature;
DROP TABLE IF EXISTS T_TypeIntervention;
DROP TABLE IF EXISTS T_Profil;
DROP TABLE IF EXISTS T_Localite;
DROP TABLE IF EXISTS T_Ville;
"""


def create_windev_tables(apps, schema_editor):
    """
    Cree les tables de synchronisation dans la base WinDev (FacturationClient).
    Utilise la connexion 'windev' directement pour contourner le router.
    Si la connexion 'windev' n'est pas configuree ou inaccessible,
    on skip silencieusement (cas du developpement local avec SQLite).
    """
    from django.db import connections
    from django.conf import settings

    # Verifier que la connexion windev est configuree
    if 'windev' not in settings.DATABASES:
        print("  [SKIP] Connexion 'windev' non configuree -- migration ignoree (dev local)")
        return

    try:
        conn = connections['windev']
        cursor = conn.cursor()

        # Executer chaque instruction separement
        for statement in FORWARD_SQL.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)

        print("  [OK] Tables de synchronisation WinDev creees avec succes")
    except Exception as e:
        print(f"  [SKIP] Impossible de creer les tables WinDev : {e}")
        print("    -> Les tables devront etre creees manuellement sur le serveur WinDev")
        print("    -> Voir docs/GUIDE_TABLES_MYSQL_WINDEV.md")


def drop_windev_tables(apps, schema_editor):
    """Supprime les tables de synchronisation (rollback)."""
    from django.db import connections
    from django.conf import settings

    if 'windev' not in settings.DATABASES:
        return

    try:
        conn = connections['windev']
        cursor = conn.cursor()
        for statement in REVERSE_SQL.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)
        print("  [OK] Tables de synchronisation WinDev supprimees")
    except Exception as e:
        print(f"  [SKIP] Impossible de supprimer les tables WinDev : {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('windev_sync', '0002_synccursor'),
    ]

    operations = [
        migrations.RunPython(
            create_windev_tables,
            drop_windev_tables,
        ),
    ]
