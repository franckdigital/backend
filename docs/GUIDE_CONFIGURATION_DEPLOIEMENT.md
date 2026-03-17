# Guide de Configuration et Déploiement — SAV Pharmacie

> Configuration complète côté **Django (VPS)** et côté **WinDev (Serveur local)**.

---

## Table des matières

1. [Architecture réseau](#1-architecture-réseau)
2. [Côté SERVEUR WINDEV — Configuration MySQL](#2-côté-serveur-windev--configuration-mysql)
3. [Côté VPS DJANGO — Installation et configuration](#3-côté-vps-django--installation-et-configuration)
4. [Lancement des services](#4-lancement-des-services)
5. [Vérification du bon fonctionnement](#5-vérification-du-bon-fonctionnement)
6. [Côté WINDEV — Code d'intégration](#6-côté-windev--code-dintégration)
7. [Développement local (Windows)](#7-développement-local-windows)
8. [Maintenance et dépannage](#8-maintenance-et-dépannage)

---

## 1. Architecture réseau

```
┌─────────────────────────────────────────┐
│           SERVEUR WINDEV                │
│         (ex: 192.168.1.100)             │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │        MySQL Server 8.x        │    │
│  │   Port 3306                     │    │
│  │                                 │    │
│  │   FacturationClient  (WinDev)   │    │
│  │   sav_pharmacie      (Django)   │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │   Application WinDev Desktop    │    │
│  │   → Accès natif MySQL           │    │
│  └─────────────────────────────────┘    │
└──────────────────┬──────────────────────┘
                   │ TCP 3306 (MySQL)
                   │ Firewall : IP du VPS uniquement
                   │
┌──────────────────▼──────────────────────┐
│             VPS DJANGO                  │
│         (ex: 51.210.xx.xx)              │
│                                         │
│  Django + Gunicorn    (port 8000)       │
│  Nginx                (port 80/443)     │
│  Redis                (port 6379)       │
│  Celery Worker + Beat                   │
└─────────────────────────────────────────┘
```

---

## 2. Côté SERVEUR WINDEV — Configuration MySQL

### 2.1 Installer MySQL Server (si pas déjà fait)

```powershell
# Windows — Télécharger MySQL Installer depuis :
# https://dev.mysql.com/downloads/installer/
# Choisir "MySQL Server 8.x" + "MySQL Workbench" (optionnel)

# Ou via Laragon (déjà inclus) :
# C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysql.exe
```

### 2.2 Créer les bases de données

```sql
-- Se connecter en tant que root
mysql -u root -p

-- Créer la base Django
CREATE DATABASE IF NOT EXISTS sav_pharmacie
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Créer la base WinDev (si pas déjà existante)
CREATE DATABASE IF NOT EXISTS FacturationClient
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

### 2.3 Créer les tables WinDev dans FacturationClient

```sql
USE FacturationClient;

-- ── Tables lues par Django (WinDev est propriétaire) ──

CREATE TABLE IF NOT EXISTS T_Ville (
    IDVille   INT AUTO_INCREMENT PRIMARY KEY,
    NomVille  VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS T_Localite (
    IDLocalite  INT AUTO_INCREMENT PRIMARY KEY,
    NomLocalite VARCHAR(255) NOT NULL,
    IDVille     INT,
    FOREIGN KEY (IDVille) REFERENCES T_Ville(IDVille),
    INDEX idx_ville (IDVille)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS T_Client (
    IDClient          INT AUTO_INCREMENT PRIMARY KEY,
    NomClient         VARCHAR(255) NOT NULL,
    TelFixe           VARCHAR(20),
    TelCel            VARCHAR(20),
    Code_2ST          VARCHAR(20),
    AdresseGeo        VARCHAR(500),
    EmailClient       VARCHAR(255),
    NomResponsable    VARCHAR(255),
    TelPharmacien     VARCHAR(20),
    SousContrat       TINYINT DEFAULT 0,
    IDLocalite        INT,
    ActifOP           TINYINT DEFAULT 1,
    DateAjout         DATETIME DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_actif (ActifOP),
    INDEX idx_date_modif (DateDernierModif),
    INDEX idx_code_2st (Code_2ST)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS T_Utilisateur (
    IDUtilisateur     INT AUTO_INCREMENT PRIMARY KEY,
    CodeUtilisateur   VARCHAR(50) NOT NULL UNIQUE,
    NomComplet        VARCHAR(255),
    TelCel            VARCHAR(20),
    telCel2           VARCHAR(20),
    ActifOP           TINYINT DEFAULT 1,
    Technicien        TINYINT DEFAULT 0,
    DateAjout         DATETIME DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tech_actif (Technicien, ActifOP),
    INDEX idx_date_modif (DateDernierModif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS T_Intervention (
    IDIntervention      INT AUTO_INCREMENT PRIMARY KEY,
    DateIntervention    DATE,
    IDClient            INT,
    IDTypeIntervention  INT,
    IDUtilisateur       INT,
    ValideOP            TINYINT DEFAULT 0,
    AnnuleOP            TINYINT DEFAULT 0,
    DateAjout           DATETIME DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (IDClient) REFERENCES T_Client(IDClient),
    FOREIGN KEY (IDUtilisateur) REFERENCES T_Utilisateur(IDUtilisateur),
    INDEX idx_annule (AnnuleOP),
    INDEX idx_client (IDClient),
    INDEX idx_date_modif (DateDernierModif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Tables partagées (Django y écrit aussi) ──

CREATE TABLE IF NOT EXISTS T_BesoinsClient (
    IDBesoinsClient     INT AUTO_INCREMENT PRIMARY KEY,
    IDClient            INT,
    DateBesoin          DATE,
    DescriptionBesoin   TEXT,
    Priorite            VARCHAR(20) DEFAULT 'normale',
    StatutBesoin        VARCHAR(50) DEFAULT 'nouveau',
    NomTechnicien       VARCHAR(255),
    SourceBesoin        VARCHAR(20) DEFAULT 'windev',
    DateAjout           DATETIME DEFAULT CURRENT_TIMESTAMP,
    DateDernierModif    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (IDClient) REFERENCES T_Client(IDClient),
    INDEX idx_source (SourceBesoin),
    INDEX idx_statut (StatutBesoin),
    INDEX idx_client (IDClient),
    INDEX idx_date_modif (DateDernierModif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS T_DetailIntervention (
    IDDetailIntervention  INT AUTO_INCREMENT PRIMARY KEY,
    IDIntervention        INT,
    Description           TEXT,
    Diagnostic            TEXT,
    ActionEffectuee       TEXT,
    PiecesUtilisees       TEXT,
    Recommandations       TEXT,
    DureeMinutes          INT DEFAULT 0,
    SourceDetail          VARCHAR(20) DEFAULT 'windev',
    DateAjout             DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IDIntervention) REFERENCES T_Intervention(IDIntervention),
    INDEX idx_source (SourceDetail),
    INDEX idx_intervention (IDIntervention)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 2.4 Créer les utilisateurs MySQL pour Django

```sql
-- ⚠️ REMPLACER les valeurs :
--   IP_DU_VPS       → IP publique du VPS Django (ex: 51.210.45.123)
--   MOT_DE_PASSE_*  → mots de passe forts

-- Utilisateur pour la base Django (lecture/écriture complète)
CREATE USER IF NOT EXISTS 'sav_app'@'IP_DU_VPS'
    IDENTIFIED BY 'MOT_DE_PASSE_APP';
GRANT ALL PRIVILEGES ON sav_pharmacie.* TO 'sav_app'@'IP_DU_VPS';

-- Utilisateur pour la synchronisation WinDev (droits restreints)
CREATE USER IF NOT EXISTS 'sav_sync'@'IP_DU_VPS'
    IDENTIFIED BY 'MOT_DE_PASSE_SYNC';

GRANT SELECT ON FacturationClient.* TO 'sav_sync'@'IP_DU_VPS';
GRANT INSERT, UPDATE ON FacturationClient.T_BesoinsClient TO 'sav_sync'@'IP_DU_VPS';
GRANT INSERT, UPDATE ON FacturationClient.T_DetailIntervention TO 'sav_sync'@'IP_DU_VPS';

FLUSH PRIVILEGES;
```

### 2.5 Configurer MySQL pour les connexions distantes

```ini
# Fichier : C:\ProgramData\MySQL\MySQL Server 8.x\my.ini
# (ou C:\laragon\bin\mysql\mysql-8.4.3-winx64\my.ini)

[mysqld]
bind-address = 0.0.0.0
port = 3306
```

```powershell
# Redémarrer MySQL après modification
net stop mysql80
net start mysql80

# Ou via Laragon : redémarrer le service MySQL depuis l'interface
```

### 2.6 Configurer le pare-feu Windows

```powershell
# ⚠️ Exécuter en tant qu'Administrateur
# Remplacer IP_DU_VPS par l'IP réelle du VPS Django

netsh advfirewall firewall add rule name="MySQL - VPS SAV Django" `
    dir=in action=allow protocol=TCP localport=3306 `
    remoteip=IP_DU_VPS
```

### 2.7 Vérifier la configuration

```powershell
# Depuis le serveur WinDev, tester les users
mysql -u sav_app -p -e "USE sav_pharmacie; SELECT 1;"
mysql -u sav_sync -p -e "USE FacturationClient; SELECT COUNT(*) FROM T_Client;"
```

---

## 3. Côté VPS DJANGO — Installation et configuration

### 3.1 Prérequis système (Ubuntu/Debian)

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances système
sudo apt install -y python3 python3-pip python3-venv \
    nginx redis-server \
    libmysqlclient-dev pkg-config \
    git curl supervisor

# Vérifier que Redis fonctionne
sudo systemctl enable redis-server
sudo systemctl start redis-server
redis-cli ping  # Doit répondre "PONG"
```

### 3.2 Cloner le projet

```bash
# Créer le dossier de l'application
sudo mkdir -p /var/www/sav-pharmacie
sudo chown $USER:$USER /var/www/sav-pharmacie

# Cloner le repo
cd /var/www/sav-pharmacie
git clone <URL_DU_REPO> backend
cd backend
```

### 3.3 Environnement virtuel Python

```bash
# Créer et activer le venv
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.4 Configurer le fichier .env

```bash
cp .env.example .env
nano .env
```

```ini
# .env — PRODUCTION

SECRET_KEY=votre-clé-secrète-très-longue-et-aléatoire
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,IP_DU_VPS

# ── Base Django (sur le MySQL du serveur WinDev) ──
DB_ENGINE=mysql
DB_NAME=sav_pharmacie
DB_USER=sav_app
DB_PASSWORD=MOT_DE_PASSE_APP
DB_HOST=IP_SERVEUR_WINDEV
DB_PORT=3306

# ── Base WinDev (sync bidirectionnelle) ──
WINDEV_DB_NAME=FacturationClient
WINDEV_DB_USER=sav_sync
WINDEV_DB_PASSWORD=MOT_DE_PASSE_SYNC
WINDEV_DB_HOST=IP_SERVEUR_WINDEV
WINDEV_DB_PORT=3306

# ── JWT ──
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# ── Email (production) ──
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-app-password

# ── CORS ──
CORS_ALLOWED_ORIGINS=https://votre-domaine.com,https://admin.votre-domaine.com

# ── Celery + Redis ──
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
SYNC_INTERVAL_SECONDS=120
```

### 3.5 Tester la connexion MySQL depuis le VPS

```bash
# Vérifier que le VPS peut joindre le MySQL du serveur WinDev
mysql -h IP_SERVEUR_WINDEV -u sav_app -p sav_pharmacie -e "SELECT 1;"
mysql -h IP_SERVEUR_WINDEV -u sav_sync -p FacturationClient -e "SELECT 1;"

# Si erreur "Can't connect" :
#   → Vérifier le firewall côté serveur WinDev (étape 2.6)
#   → Vérifier bind-address dans my.ini (étape 2.5)
#   → Vérifier que le port 3306 est ouvert : telnet IP_SERVEUR_WINDEV 3306
```

### 3.6 Migrations et données initiales

```bash
cd /var/www/sav-pharmacie/backend
source venv/bin/activate

# Appliquer les migrations sur sav_pharmacie
python manage.py migrate

# Créer le superutilisateur admin
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Première synchronisation manuelle depuis WinDev
python manage.py sync_windev
```

### 3.7 Configurer Gunicorn

```bash
# Tester Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Créer le fichier systemd :

```bash
sudo nano /etc/systemd/system/sav-gunicorn.service
```

```ini
[Unit]
Description=SAV Pharmacie Django (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sav-pharmacie/backend
ExecStart=/var/www/sav-pharmacie/backend/venv/bin/gunicorn \
    config.wsgi:application \
    --bind unix:/var/www/sav-pharmacie/backend/gunicorn.sock \
    --workers 3 \
    --timeout 120 \
    --access-logfile /var/log/sav/gunicorn-access.log \
    --error-logfile /var/log/sav/gunicorn-error.log
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /var/log/sav
sudo chown www-data:www-data /var/log/sav

sudo systemctl daemon-reload
sudo systemctl enable sav-gunicorn
sudo systemctl start sav-gunicorn
sudo systemctl status sav-gunicorn
```

### 3.8 Configurer Celery Worker + Beat

```bash
sudo nano /etc/systemd/system/sav-celery-worker.service
```

```ini
[Unit]
Description=SAV Pharmacie Celery Worker
After=network.target redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sav-pharmacie/backend
ExecStart=/var/www/sav-pharmacie/backend/venv/bin/celery \
    -A config worker \
    --loglevel=info \
    --concurrency=2 \
    --logfile=/var/log/sav/celery-worker.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo nano /etc/systemd/system/sav-celery-beat.service
```

```ini
[Unit]
Description=SAV Pharmacie Celery Beat (scheduler sync toutes les 2 min)
After=network.target redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sav-pharmacie/backend
ExecStart=/var/www/sav-pharmacie/backend/venv/bin/celery \
    -A config beat \
    --loglevel=info \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler \
    --logfile=/var/log/sav/celery-beat.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload

sudo systemctl enable sav-celery-worker
sudo systemctl start sav-celery-worker

sudo systemctl enable sav-celery-beat
sudo systemctl start sav-celery-beat

# Vérifier
sudo systemctl status sav-celery-worker
sudo systemctl status sav-celery-beat
```

### 3.9 Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/sav-pharmacie
```

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    # Rediriger HTTP → HTTPS (activer après Certbot)
    # return 301 https://$host$request_uri;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/sav-pharmacie/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/sav-pharmacie/backend/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/sav-pharmacie/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/sav-pharmacie /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL avec Certbot (optionnel mais recommandé)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

---

## 4. Lancement des services

### 4.1 Côté Serveur WinDev

```powershell
# 1. Démarrer MySQL
net start mysql80
# ou via Laragon : démarrer le service

# 2. Vérifier que les bases existent
mysql -u root -p -e "SHOW DATABASES;"
# Doit afficher : FacturationClient, sav_pharmacie

# 3. Vérifier les tables
mysql -u root -p FacturationClient -e "SHOW TABLES;"
# Doit afficher : T_BesoinsClient, T_Client, T_DetailIntervention,
#                 T_Intervention, T_Localite, T_Utilisateur, T_Ville

# 4. Lancer l'application WinDev
# → Ouvrir normalement depuis le raccourci / exécutable
```

### 4.2 Côté VPS Django

```bash
# ── Démarrer tous les services ──

# Redis (broker Celery)
sudo systemctl start redis-server

# Django (Gunicorn)
sudo systemctl start sav-gunicorn

# Celery Worker (exécute les tâches de sync)
sudo systemctl start sav-celery-worker

# Celery Beat (planifie les tâches toutes les 2 min)
sudo systemctl start sav-celery-beat

# Nginx (reverse proxy)
sudo systemctl start nginx

# ── Vérifier que tout tourne ──
sudo systemctl status sav-gunicorn sav-celery-worker sav-celery-beat redis-server nginx
```

### 4.3 Arrêter tous les services

```bash
sudo systemctl stop sav-celery-beat sav-celery-worker sav-gunicorn
```

### 4.4 Redémarrer après une mise à jour du code

```bash
cd /var/www/sav-pharmacie/backend
source venv/bin/activate

git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart sav-gunicorn sav-celery-worker sav-celery-beat
```

---

## 5. Vérification du bon fonctionnement

### 5.1 Tester l'API Django

```bash
# Depuis le VPS
curl http://localhost:8000/api/v1/schema/ -I
# HTTP 200 OK

# Depuis l'extérieur
curl https://votre-domaine.com/api/v1/schema/ -I
```

### 5.2 Vérifier la synchronisation

```bash
# Synchronisation manuelle
cd /var/www/sav-pharmacie/backend
source venv/bin/activate

# WinDev → Django
python manage.py sync_windev --windev-to-django

# Django → WinDev
python manage.py sync_windev --django-to-windev

# Sync complète
python manage.py sync_windev

# Voir les curseurs de sync
python manage.py shell -c "
from apps.windev_sync.models import SyncCursor
for c in SyncCursor.objects.all():
    print(f'{c.entity_type} ({c.direction}): ID={c.last_synced_id}, date={c.last_synced_at}')
"
```

### 5.3 Vérifier les tâches Celery

```bash
# Voir les workers actifs
celery -A config inspect active

# Voir les tâches planifiées par Beat
celery -A config inspect scheduled

# Voir les logs
tail -f /var/log/sav/celery-worker.log
tail -f /var/log/sav/celery-beat.log
```

### 5.4 Vérifier via l'API (authentifié)

```bash
# Obtenir un token JWT
TOKEN=$(curl -s -X POST https://votre-domaine.com/api/v1/auth/token/ \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"votre-password"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

# État de la synchronisation
curl -s https://votre-domaine.com/api/v1/windev/status/ \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Logs de sync
curl -s https://votre-domaine.com/api/v1/windev/logs/ \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Curseurs
curl -s https://votre-domaine.com/api/v1/windev/cursors/ \
    -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## 6. Côté WINDEV — Code d'intégration

### 6.0 Architecture HFSQL + MySQL (coexistence)

WinDev utilise **deux moteurs de base de données simultanément** :

```
Application WinDev
    |
    |-- HFSQL (Classic ou Client/Server) -- automatique, pas de config
    |     Tables locales : logs, cache, preferences utilisateur, params UI
    |     Fichiers .fic/.ndx/.mmo sur le disque local
    |
    |-- MySQL (via Connecteur Natif) -- connexion explicite
          Base : FacturationClient (91 tables)
          Tables metier partagees avec Django
          Connexion locale (127.0.0.1:3306)
```

**Principe** :
- Les tables **sans `HChangeConnexion`** restent en **HFSQL** (comportement par defaut)
- Les tables avec `HChangeConnexion(table, gConnMySQL)` utilisent **MySQL**
- Les deux moteurs fonctionnent **en parallele** dans le meme code

**Prerequis** :
1. Activer le **Connecteur Natif MySQL** dans WinDev :
   - Menu **Projet** > **Description du projet** > onglet **Fichiers**
   - Cocher **"Connecteur Natif MySQL"**
   - Distribuer `wd290mysql.dll` avec l'executable
2. MySQL Server doit etre installe et la base `FacturationClient` doit exister

### 6.1 Initialisation de la connexion MySQL

```
// ── Projet WinDev : Code d'initialisation ──
// Ce code se place dans l'evenement "Initialisation" du projet

// ═══════════════════════════════════════════
// HFSQL : rien a faire, automatique
// Les tables HFSQL locales (T_LogLocal, T_Preferences...)
// utilisent les fichiers .fic par defaut
// ═══════════════════════════════════════════

// ═══════════════════════════════════════════
// MySQL : connexion explicite a FacturationClient
// ═══════════════════════════════════════════
gsConnMySQL est une Connexion

gsConnMySQL.Fournisseur     = hAccesNatifMySQL
gsConnMySQL.Serveur         = "127.0.0.1"       // MySQL local sur le meme serveur
gsConnMySQL.Utilisateur     = "root"
gsConnMySQL.MotDePasse      = ""
gsConnMySQL.BaseDeDonnees   = "FacturationClient"
gsConnMySQL.Port            = 3306

SI PAS HOuvreConnexion(gsConnMySQL) ALORS
    Erreur("Connexion MySQL impossible : " + HErreurInfo())
    FinProgramme()
FIN

// ═══════════════════════════════════════════
// Associer les tables metier a MySQL
// (toutes les 91 tables de FacturationClient)
// ═══════════════════════════════════════════

// -- Tables de synchronisation avec Django --
HChangeConnexion(T_Client, gsConnMySQL)
HChangeConnexion(T_Utilisateur, gsConnMySQL)
HChangeConnexion(T_Intervention, gsConnMySQL)
HChangeConnexion(T_BesoinsClient, gsConnMySQL)
HChangeConnexion(T_DetailIntervention, gsConnMySQL)
HChangeConnexion(T_Ville, gsConnMySQL)
HChangeConnexion(T_Localite, gsConnMySQL)
HChangeConnexion(T_TypeIntervention, gsConnMySQL)
HChangeConnexion(T_Nature, gsConnMySQL)
HChangeConnexion(T_Nature_TypeIntervention, gsConnMySQL)

// -- Tables metier (non synchronisees avec Django) --
HChangeConnexion(T_produit, gsConnMySQL)
HChangeConnexion(T_fournisseur, gsConnMySQL)
HChangeConnexion(T_Factures, gsConnMySQL)
HChangeConnexion(T_lignes, gsConnMySQL)
HChangeConnexion(T_Contrat, gsConnMySQL)
HChangeConnexion(T_commande, gsConnMySQL)
HChangeConnexion(t_CommandeLigne, gsConnMySQL)
HChangeConnexion(T_Caisse, gsConnMySQL)
HChangeConnexion(T_reglement, gsConnMySQL)
HChangeConnexion(T_Mouvement, gsConnMySQL)
HChangeConnexion(t_MouvementLigne, gsConnMySQL)
HChangeConnexion(T_inventaire, gsConnMySQL)
HChangeConnexion(T_SessionCaisse, gsConnMySQL)
HChangeConnexion(T_Billetage, gsConnMySQL)
HChangeConnexion(T_Depense, gsConnMySQL)
HChangeConnexion(T_Cloture_Journal, gsConnMySQL)
// ... (toutes les autres tables de FacturationClient)

// Creer les tables si elles n'existent pas encore
HCreationSiInexistant(T_Client)
HCreationSiInexistant(T_Utilisateur)
HCreationSiInexistant(T_Intervention)
HCreationSiInexistant(T_BesoinsClient)
HCreationSiInexistant(T_DetailIntervention)
HCreationSiInexistant(T_Ville)
HCreationSiInexistant(T_Localite)
```

### 6.1b Utilisation parallele HFSQL + MySQL

```
// ═══════════════════════════════════════════
// Exemple : creer un client dans MySQL
// ET ecrire un log dans HFSQL en meme temps
// ═══════════════════════════════════════════

// --- Ecriture MySQL (T_Client) ---
HRaZ(T_Client)
T_Client.NomClient       = SAI_NomPharmacie
T_Client.TelCel          = SAI_Telephone
T_Client.EmailClient     = SAI_Email
T_Client.NomResponsable  = SAI_Pharmacien
T_Client.IDLocalite      = COMBO_Localite
T_Client.ActifOP         = 1
T_Client.SousContrat     = 1
T_Client.DateAjout       = DateDuJour()
T_Client.DateDernierModif = DateDuJour()
HAjoute(T_Client)
// -> s'ecrit dans MySQL FacturationClient
// -> Django le detectera a la prochaine synchronisation

// --- Ecriture HFSQL (log local) ---
HRaZ(T_LogLocal)
T_LogLocal.Action    = "Creation client : " + SAI_NomPharmacie
T_LogLocal.Date      = DateDuJour()
T_LogLocal.Heure     = HeureSys()
T_LogLocal.Operateur = gpclUtilisateurCourant.Code
HAjoute(T_LogLocal)
// -> s'ecrit dans HFSQL local (.fic)
// -> invisible pour Django, usage interne WinDev uniquement
```

### 6.2 Écriture avec marquage de source

```
// ── Ajouter un besoin client (WinDev) ──
HRAZRubrique(T_BesoinsClient)
T_BesoinsClient.IDClient          = nIDClient
T_BesoinsClient.DateBesoin        = DateDuJour()
T_BesoinsClient.DescriptionBesoin = sDescription
T_BesoinsClient.Priorite          = "normale"
T_BesoinsClient.StatutBesoin      = "nouveau"
T_BesoinsClient.SourceBesoin      = "windev"     // ← OBLIGATOIRE
HAjoute(T_BesoinsClient)


// ── Ajouter un détail d'intervention (WinDev) ──
HRAZRubrique(T_DetailIntervention)
T_DetailIntervention.IDIntervention   = nIDIntervention
T_DetailIntervention.Description      = sDescription
T_DetailIntervention.Diagnostic       = sDiagnostic
T_DetailIntervention.ActionEffectuee  = sAction
T_DetailIntervention.SourceDetail     = "windev"  // ← OBLIGATOIRE
HAjoute(T_DetailIntervention)
```

### 6.3 Lire les données créées par Django

```
// ── Afficher les tickets SAV créés depuis l'app web ──
sRequête est une chaîne = [
    SELECT IDBesoinsClient, IDClient, DateBesoin,
           DescriptionBesoin, Priorite, StatutBesoin, NomTechnicien
    FROM T_BesoinsClient
    WHERE SourceBesoin = 'web'
    ORDER BY DateAjout DESC
    LIMIT 50
]

HExécuteRequêteSQL(REQ_TicketsWeb, gsConnMySQL, sRequête)
HLitPremier(REQ_TicketsWeb)
TANTQUE PAS HEnDehors(REQ_TicketsWeb)
    // Afficher dans un tableau / liste
    TableAjouteLigne(TABLE_TicketsWeb,
        REQ_TicketsWeb.IDBesoinsClient,
        REQ_TicketsWeb.DateBesoin,
        REQ_TicketsWeb.DescriptionBesoin,
        REQ_TicketsWeb.Priorite,
        REQ_TicketsWeb.StatutBesoin)
    HLitSuivant(REQ_TicketsWeb)
FIN
HLibèreRequête(REQ_TicketsWeb)
```

### 6.4 Protection : ne pas modifier les données Django

```
// ── Avant de modifier un besoin, vérifier la source ──
PROCEDURE ModifierBesoin(nIDBesoin, sNouveauStatut)

HLitRecherchePremier(T_BesoinsClient, IDBesoinsClient, nIDBesoin)
SI HEnDehors() ALORS
    Erreur("Besoin introuvable.")
    RETOUR
FIN

SI T_BesoinsClient.SourceBesoin = "web" ALORS
    Erreur("Ce besoin provient de l'application web." + RC + ...
           "Modification interdite depuis WinDev.")
    RETOUR
FIN

// OK — besoin WinDev, on peut modifier
T_BesoinsClient.StatutBesoin      = sNouveauStatut
T_BesoinsClient.DateDernierModif  = DateHeureSys()
HModifie(T_BesoinsClient)
Info("Besoin mis à jour.")
```

### 6.5 Modifier un client (avec DateDernierModif)

```
// ⚠️ Toujours mettre à jour DateDernierModif pour que Django détecte le changement

PROCEDURE ModifierClient(nIDClient, sNouveauNom, sTel)

HLitRecherchePremier(T_Client, IDClient, nIDClient)
SI HEnDehors() ALORS RETOUR

T_Client.NomClient        = sNouveauNom
T_Client.TelCel           = sTel
T_Client.DateDernierModif = DateHeureSys()   // ← OBLIGATOIRE
HModifie(T_Client)
```

---

## 7. Développement local (Windows)

### 7.1 Prérequis

- Python 3.11+
- Laragon (MySQL 8.x inclus) ou MySQL Server
- Redis pour Windows (optionnel, pour Celery local)
- Git

### 7.2 Installation rapide

```powershell
# Cloner et configurer
cd C:\Users\HP\Desktop\projets\sav-pharmacie-vite
cd backend

# Créer le venv
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 7.3 Configurer .env local

```ini
# .env — DÉVELOPPEMENT LOCAL
SECRET_KEY=django-insecure-dev-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=mysql
DB_NAME=sav_pharmacie
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306

# WinDev local (optionnel, laisser vide si pas de base WinDev en local)
WINDEV_DB_NAME=FacturationClient
WINDEV_DB_USER=root
WINDEV_DB_PASSWORD=
WINDEV_DB_HOST=127.0.0.1
WINDEV_DB_PORT=3306

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

### 7.4 Créer la base et migrer

```powershell
# Via Laragon MySQL (ou mysql client)
& "C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS sav_pharmacie CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Migrer
venv\Scripts\python manage.py migrate

# Créer l'admin
venv\Scripts\python manage.py createsuperuser
```

### 7.5 Lancer le serveur Django

```powershell
venv\Scripts\python manage.py runserver
# → http://127.0.0.1:8000
```

### 7.6 Lancer Celery en local (optionnel)

```powershell
# Terminal 1 : Worker
venv\Scripts\celery -A config worker --loglevel=info --pool=solo

# Terminal 2 : Beat (scheduler)
venv\Scripts\celery -A config beat --loglevel=info

# Ou les deux ensemble (dev uniquement)
venv\Scripts\celery -A config worker -B --loglevel=info --pool=solo
```

> **Note** : Sur Windows, Celery nécessite `--pool=solo` ou `--pool=threads`.

### 7.7 Sync manuelle (sans Celery)

```powershell
# Si pas de Redis/Celery en local
venv\Scripts\python manage.py sync_windev
venv\Scripts\python manage.py sync_windev --windev-to-django
venv\Scripts\python manage.py sync_windev --django-to-windev
```

---

## 8. Maintenance et dépannage

### 8.1 Commandes de maintenance Django

```bash
# ── Synchronisation ──
python manage.py sync_windev                    # Sync complète
python manage.py sync_windev --windev-to-django # WD → DJ
python manage.py sync_windev --django-to-windev # DJ → WD
python manage.py sync_windev --referentials     # Référentiels
python manage.py sync_windev --reset-cursors    # Reset (force re-sync)

# ── Base de données ──
python manage.py migrate                        # Appliquer les migrations
python manage.py makemigrations                 # Détecter les changements
python manage.py dbshell                        # Console MySQL interactive
python manage.py showmigrations                 # Voir l'état des migrations

# ── Utilisateurs ──
python manage.py createsuperuser                # Créer un admin
python manage.py changepassword <username>      # Changer un mot de passe

# ── Statiques ──
python manage.py collectstatic --noinput        # Collecter les fichiers statiques
```

### 8.2 Logs à surveiller

```bash
# Django / Gunicorn
tail -f /var/log/sav/gunicorn-access.log
tail -f /var/log/sav/gunicorn-error.log

# Celery Worker (sync tasks)
tail -f /var/log/sav/celery-worker.log

# Celery Beat (scheduler)
tail -f /var/log/sav/celery-beat.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 8.3 Problèmes courants

| Problème | Cause probable | Solution |
|---|---|---|
| `Can't connect to MySQL` depuis VPS | Firewall ou bind-address | Vérifier étapes 2.5 et 2.6 |
| `Access denied for user 'sav_sync'` | Mauvais password ou IP | Recréer l'utilisateur MySQL avec la bonne IP |
| Sync ne se lance pas | Celery Beat arrêté | `sudo systemctl restart sav-celery-beat` |
| Sync en erreur | Table manquante côté WinDev | Créer les tables (étape 2.3) |
| Données WinDev pas visibles | Sync pas encore passée | Attendre 2 min ou lancer manuellement |
| `SyncCursor` bloqué | Erreur lors d'une sync | `python manage.py sync_windev --reset-cursors` |
| Celery `pool=prefork` crash Windows | Windows ne supporte pas prefork | Utiliser `--pool=solo` ou `--pool=threads` |
| `FOREIGN KEY constraint fails` | IDClient inexistant | Synchroniser les clients avant les besoins |

### 8.4 Ordre de synchronisation

```
1. T_Ville       → Region         (référentiels, pas de dépendance)
2. T_Localite    → Commune        (dépend de T_Ville)
3. T_Client      → Pharmacie      (dépend de T_Localite)
4. T_Utilisateur → User/Technicien (pas de dépendance)
5. T_Intervention→ Ticket          (dépend de T_Client + T_Utilisateur)
6. T_BesoinsClient→ Ticket         (dépend de T_Client)
7. Ticket → T_BesoinsClient        (Django → WinDev, dépend de T_Client)
8. Rapport → T_DetailIntervention   (Django → WinDev, dépend de T_Intervention)
```

### 8.5 Sauvegarde des bases

```bash
# Depuis le serveur WinDev — sauvegarder les deux bases
mysqldump -u root -p sav_pharmacie > /backup/sav_pharmacie_$(date +%Y%m%d).sql
mysqldump -u root -p FacturationClient > /backup/FacturationClient_$(date +%Y%m%d).sql

# Crontab de sauvegarde quotidienne (sur le serveur WinDev)
0 2 * * * mysqldump -u root sav_pharmacie | gzip > /backup/sav_pharmacie_$(date +\%Y\%m\%d).sql.gz
0 2 * * * mysqldump -u root FacturationClient | gzip > /backup/FacturationClient_$(date +\%Y\%m\%d).sql.gz
```

---

## Récapitulatif des services

| Service | Localisation | Port | Rôle |
|---|---|---|---|
| MySQL Server | Serveur WinDev | 3306 | Base de données (2 bases) |
| App WinDev | Serveur WinDev | — | Application desktop |
| Nginx | VPS Django | 80/443 | Reverse proxy + SSL |
| Gunicorn | VPS Django | socket | Serveur WSGI Django |
| Redis | VPS Django | 6379 | Broker Celery |
| Celery Worker | VPS Django | — | Exécute les tâches de sync |
| Celery Beat | VPS Django | — | Planifie les tâches (toutes les 2 min) |
