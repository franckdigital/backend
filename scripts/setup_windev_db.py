"""
Script de setup : creation de la base FacturationClient + tables de synchronisation.

Usage :
    python scripts/setup_windev_db.py

Ce script :
1. Cree la base de donnees FacturationClient si elle n'existe pas
2. Cree l'utilisateur sav_sync avec les droits necessaires
3. Cree toutes les tables de synchronisation (schema reel WinDev)
4. Insere les donnees de reference initiales
5. Lance la migration Django 0003 pour marquer la migration comme appliquee

Prerequis : MySQL accessible en root (Laragon / XAMPP / MySQL Server)
"""

import os
import sys
import subprocess

# Detecter le chemin mysql.exe
MYSQL_PATHS = [
    r"C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysql.exe",
    r"C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin\mysql.exe",
    r"C:\xampp\mysql\bin\mysql.exe",
    r"C:\wamp64\bin\mysql\mysql8.0.31\bin\mysql.exe",
    r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
    r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe",
]

MYSQL_EXE = None
for path in MYSQL_PATHS:
    if os.path.exists(path):
        MYSQL_EXE = path
        break

if not MYSQL_EXE:
    # Tenter de trouver mysql.exe automatiquement
    for root_dir in [r"C:\laragon\bin\mysql", r"C:\Program Files\MySQL"]:
        if os.path.exists(root_dir):
            for dirpath, dirnames, filenames in os.walk(root_dir):
                if "mysql.exe" in filenames:
                    MYSQL_EXE = os.path.join(dirpath, "mysql.exe")
                    break
        if MYSQL_EXE:
            break

if not MYSQL_EXE:
    print("[ERREUR] mysql.exe introuvable. Ajoutez MySQL au PATH ou modifiez MYSQL_PATHS dans ce script.")
    sys.exit(1)

print(f"[INFO] MySQL trouve : {MYSQL_EXE}")

# Configuration
MYSQL_USER = "root"
MYSQL_PASSWORD = ""  # vide pour Laragon par defaut
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = "3306"

DB_NAME = "FacturationClient"
SYNC_USER = "sav_sync"
SYNC_PASSWORD = "sav_sync_2024!"  # Changer en production


def run_sql(sql, database=None, description=""):
    """Execute du SQL via mysql.exe."""
    cmd = [MYSQL_EXE, f"-u{MYSQL_USER}", f"-h{MYSQL_HOST}", f"-P{MYSQL_PORT}"]
    if MYSQL_PASSWORD:
        cmd.append(f"-p{MYSQL_PASSWORD}")
    if database:
        cmd.append(database)

    result = subprocess.run(
        cmd,
        input=sql,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        print(f"  [ERREUR] {description}: {result.stderr.strip()}")
        return False
    else:
        if description:
            print(f"  [OK] {description}")
        return True


# ============================================================
# ETAPE 1 : Creer la base de donnees
# ============================================================
print("\n" + "=" * 60)
print("ETAPE 1 : Creation de la base de donnees FacturationClient")
print("=" * 60)

run_sql(
    f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
    description=f"Base {DB_NAME} creee"
)


# ============================================================
# ETAPE 2 : Creer l'utilisateur sav_sync
# ============================================================
print("\n" + "=" * 60)
print("ETAPE 2 : Creation de l'utilisateur sav_sync")
print("=" * 60)

run_sql(f"""
    CREATE USER IF NOT EXISTS '{SYNC_USER}'@'127.0.0.1'
        IDENTIFIED BY '{SYNC_PASSWORD}';
    CREATE USER IF NOT EXISTS '{SYNC_USER}'@'localhost'
        IDENTIFIED BY '{SYNC_PASSWORD}';

    -- Lecture sur toute la base WinDev
    GRANT SELECT ON `{DB_NAME}`.* TO '{SYNC_USER}'@'127.0.0.1';
    GRANT SELECT ON `{DB_NAME}`.* TO '{SYNC_USER}'@'localhost';

    FLUSH PRIVILEGES;
""", description="Utilisateur sav_sync cree avec SELECT")


# ============================================================
# ETAPE 3 : Creer les tables
# ============================================================
print("\n" + "=" * 60)
print("ETAPE 3 : Creation des tables de synchronisation")
print("=" * 60)

TABLES_SQL = """

-- ============================================================
-- REFERENTIELS
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
-- TABLES METIER (lues par Django, gerees par WinDev)
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

"""

run_sql(TABLES_SQL, database=DB_NAME, description="Tables de synchronisation creees")

# Appliquer les droits INSERT/UPDATE maintenant que les tables existent
print("\n  Application des droits INSERT/UPDATE sur les tables de sync...")
run_sql(f"""
    GRANT INSERT, UPDATE ON `{DB_NAME}`.`T_BesoinsClient`
        TO '{SYNC_USER}'@'127.0.0.1';
    GRANT INSERT, UPDATE ON `{DB_NAME}`.`T_BesoinsClient`
        TO '{SYNC_USER}'@'localhost';
    GRANT INSERT, UPDATE ON `{DB_NAME}`.`T_DetailIntervention`
        TO '{SYNC_USER}'@'127.0.0.1';
    GRANT INSERT, UPDATE ON `{DB_NAME}`.`T_DetailIntervention`
        TO '{SYNC_USER}'@'localhost';
    FLUSH PRIVILEGES;
""", description="Droits INSERT/UPDATE appliques sur T_BesoinsClient et T_DetailIntervention")


# ============================================================
# ETAPE 4 : Donnees de reference
# ============================================================
print("\n" + "=" * 60)
print("ETAPE 4 : Insertion des donnees de reference")
print("=" * 60)

SEED_SQL = """
INSERT IGNORE INTO T_TypeIntervention (IDTypeIntervention, LibTypeIntervention) VALUES
    ('DEPANNAGE', 'Depannage'),
    ('MIXTE', 'Mixte'),
    ('INVENTAIRE', 'Inventaire'),
    ('MAINTENANCE', 'Maintenance'),
    ('MAJ', 'Mise a jour');

INSERT IGNORE INTO T_Profil (IDProfil, LibProfil) VALUES
    ('ADMIN', 'Administrateur'),
    ('TECH', 'Technicien'),
    ('SAISIE', 'Saisie');

INSERT IGNORE INTO T_Nature (LibNature) VALUES
    ('Logiciel'),
    ('Materiel'),
    ('Reseau'),
    ('Formation'),
    ('Installation');

INSERT IGNORE INTO T_Ville (NomVille) VALUES
    ('Abidjan'),
    ('Bouake'),
    ('Yamoussoukro'),
    ('San Pedro'),
    ('Daloa'),
    ('Korhogo'),
    ('Man');

INSERT IGNORE INTO T_Localite (NomLocalite, IDVille) VALUES
    ('Cocody', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Abidjan')),
    ('Plateau', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Abidjan')),
    ('Marcory', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Abidjan')),
    ('Yopougon', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Abidjan')),
    ('Treichville', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Abidjan')),
    ('Abobo', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Abidjan')),
    ('Adjame', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Abidjan')),
    ('Centre', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Bouake')),
    ('Centre', (SELECT IDVille FROM T_Ville WHERE NomVille = 'Yamoussoukro'));
"""

run_sql(SEED_SQL, database=DB_NAME, description="Donnees de reference inserees")


# ============================================================
# ETAPE 5 : Donnees de test (clients + techniciens)
# ============================================================
print("\n" + "=" * 60)
print("ETAPE 5 : Insertion de donnees de test")
print("=" * 60)

TEST_SQL = """
-- Utilisateurs / Techniciens de test
INSERT IGNORE INTO T_Utilisateur (CodeUtilisateur, NomComplet, TelCel, Technicien, ActifOP, Disponible, IDProfil) VALUES
    ('TECH001', 'Kouame Jean', '0701020304', 1, 1, 1, 'TECH'),
    ('TECH002', 'Traore Moussa', '0705060708', 1, 1, 1, 'TECH'),
    ('TECH003', 'Kone Issa', '0709101112', 1, 1, 0, 'TECH'),
    ('ADMIN01', 'Diallo Admin', '0700000001', 0, 1, 1, 'ADMIN');

-- Clients / Pharmacies de test
INSERT IGNORE INTO T_Client (NomClient, Code_2ST, TelFixe, TelCel, AdresseGeo, EmailClient, NomResponsable, TelPharmacien, SousContrat, ActifOP, InterieurPays, IDLocalite) VALUES
    ('Pharmacie du Plateau', 'PL001', '20222334', '0707080910', 'Plateau, Rue du Commerce', 'plateau@pharma.ci', 'Dr Konan', '0707080910', 1, 1, 0,
        (SELECT IDLocalite FROM T_Localite WHERE NomLocalite = 'Plateau' LIMIT 1)),
    ('Pharmacie de Cocody', 'CO002', '20334455', '0701234567', 'Cocody, Angre', 'cocody@pharma.ci', 'Dr Bamba', '0701234567', 1, 1, 0,
        (SELECT IDLocalite FROM T_Localite WHERE NomLocalite = 'Cocody' LIMIT 1)),
    ('Pharmacie Yopougon Centre', 'YO003', '20556677', '0709876543', 'Yopougon, Marche', 'yop@pharma.ci', 'Dr Coulibaly', '0709876543', 0, 1, 0,
        (SELECT IDLocalite FROM T_Localite WHERE NomLocalite = 'Yopougon' LIMIT 1)),
    ('Pharmacie Bouake Nord', 'BK004', '20887766', '0704443322', 'Bouake Centre', 'bouake@pharma.ci', 'Dr Toure', '0704443322', 1, 1, 1,
        (SELECT IDLocalite FROM T_Localite WHERE NomLocalite = 'Centre' AND IDVille = (SELECT IDVille FROM T_Ville WHERE NomVille = 'Bouake') LIMIT 1));

-- Interventions de test
INSERT IGNORE INTO T_Intervention (DateIntervention, IDClient, IDTypeIntervention, IDUtilisateur, ValideOP, EffectueOP, NbJours, MontantTTC) VALUES
    (CURDATE(), 1, 'DEPANNAGE', 1, 1, 0, 1, 50000),
    (DATE_SUB(CURDATE(), INTERVAL 3 DAY), 2, 'MAINTENANCE', 2, 1, 1, 2, 150000),
    (DATE_SUB(CURDATE(), INTERVAL 1 DAY), 3, 'MAJ', 1, 0, 0, 1, 25000);

-- Besoins de test
INSERT IGNORE INTO T_BesoinsClient (DateBesoin, DescriptionBesoin, IDClient, NomTechnicien, ValideOP, Traite, Annule, IDUtilisateur) VALUES
    (CURDATE(), 'Ecran de caisse ne repond plus apres mise a jour', 1, 'Kouame Jean', 1, 0, 0, 1),
    (DATE_SUB(CURDATE(), INTERVAL 2 DAY), 'Imprimante ticket ne fonctionne plus', 2, '', 0, 0, 0, 0),
    (DATE_SUB(CURDATE(), INTERVAL 5 DAY), 'Demande formation nouveau module inventaire', 3, 'Traore Moussa', 1, 1, 0, 2);

-- Detail intervention de test
INSERT IGNORE INTO T_DetailIntervention (IDIntervention, IDNature, DescriptionDetail, IDUtilisateur) VALUES
    (2, 1, 'Remplacement disque dur + reinstallation systeme. Sauvegarde effectuee.', 2);
"""

run_sql(TEST_SQL, database=DB_NAME, description="Donnees de test inserees")


# ============================================================
# ETAPE 6 : Verification
# ============================================================
print("\n" + "=" * 60)
print("ETAPE 6 : Verification")
print("=" * 60)

run_sql(
    "SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES "
    f"WHERE TABLE_SCHEMA = '{DB_NAME}' ORDER BY TABLE_NAME;",
    description="Liste des tables"
)

# Afficher le resultat
cmd = [MYSQL_EXE, f"-u{MYSQL_USER}", f"-h{MYSQL_HOST}", f"-P{MYSQL_PORT}"]
if MYSQL_PASSWORD:
    cmd.append(f"-p{MYSQL_PASSWORD}")
cmd.extend(["-e",
    f"SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.TABLES "
    f"WHERE TABLE_SCHEMA = '{DB_NAME}' ORDER BY TABLE_NAME;"
])

result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if result.returncode == 0:
    print(result.stdout)
else:
    print(f"  [ERREUR] {result.stderr}")


# ============================================================
# ETAPE 7 : Mise a jour du .env
# ============================================================
print("=" * 60)
print("ETAPE 7 : Verification du .env")
print("=" * 60)

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        content = f.read()

    needs_update = False

    if "WINDEV_DB_PASSWORD=" in content and f"WINDEV_DB_PASSWORD={SYNC_PASSWORD}" not in content:
        content = content.replace(
            "WINDEV_DB_PASSWORD=",
            f"WINDEV_DB_PASSWORD={SYNC_PASSWORD}"
        )
        needs_update = True

    if needs_update:
        with open(env_path, "w") as f:
            f.write(content)
        print(f"  [OK] .env mis a jour avec le mot de passe sav_sync")
    else:
        print(f"  [OK] .env deja configure")
else:
    print(f"  [INFO] Fichier .env non trouve a {env_path}")


print("\n" + "=" * 60)
print("SETUP TERMINE !")
print("=" * 60)
print(f"""
Base de donnees : {DB_NAME}
Utilisateur sync: {SYNC_USER} / {SYNC_PASSWORD}
Tables creees   : 10 tables (referentiels + metier + sync)
Donnees test    : 4 clients, 4 techniciens, 3 interventions, 3 besoins

Prochaine etape :
  python manage.py migrate
  python manage.py sync_windev
""")
