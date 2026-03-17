# Guide de Déploiement Production - SAV Pharmacie API

> **Domaine** : `api-magicsuite.numerix.digital`  
> **IP Serveur** : `72.60.88.93`  
> **OS recommandé** : Ubuntu 22.04 / 24.04 LTS

---

## Table des matières

1. [Connexion au serveur](#1-connexion-au-serveur)
2. [Mise à jour système et paquets](#2-mise-à-jour-système-et-paquets)
3. [Installation MySQL](#3-installation-mysql)
4. [Installation phpMyAdmin](#4-installation-phpmyadmin)
5. [Préparation du projet Django](#5-préparation-du-projet-django)
6. [Configuration .env production](#6-configuration-env-production)
7. [Gunicorn - Serveur WSGI](#7-gunicorn---serveur-wsgi)
8. [Nginx - Reverse Proxy](#8-nginx---reverse-proxy)
9. [Certbot - SSL/HTTPS](#9-certbot---sslhttps)
10. [Redis + Celery](#10-redis--celery)
11. [Firewall (UFW)](#11-firewall-ufw)
12. [Commandes de maintenance](#12-commandes-de-maintenance)

---

## 1. Connexion au serveur

```bash
ssh root@72.60.88.93
```

---

## 2. Mise à jour système et paquets

```bash
# Mise à jour du système
apt update && apt upgrade -y

# Paquets essentiels
apt install -y python3 python3-pip python3-venv python3-dev \
  build-essential libmysqlclient-dev pkg-config \
  nginx certbot python3-certbot-nginx \
  git curl wget unzip supervisor \
  redis-server

# Vérifications
python3 --version
nginx -v
redis-cli ping
```

---

## 3. Installation MySQL

```bash
# Installation
apt install -y mysql-server mysql-client

# Sécurisation
mysql_secure_installation
# → Répondre Y à toutes les questions (mot de passe root, supprimer users anonymes, etc.)

# Connexion MySQL
mysql -u root -p

# Créer la base et l'utilisateur
CREATE DATABASE sav_pharmacie CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sav_user'@'localhost' IDENTIFIED BY 'MOT_DE_PASSE_FORT_ICI';
GRANT ALL PRIVILEGES ON sav_pharmacie.* TO 'sav_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 4. Installation phpMyAdmin

```bash
# Installation
apt install -y phpmyadmin

# Pendant l'installation :
# → Choisir "apache2" ou "aucun" (on utilise nginx)
# → Configurer la base avec dbconfig-common : Oui
# → Mot de passe phpMyAdmin

# Si vous avez choisi "aucun" pour le serveur web, installer php-fpm :
apt install -y php-fpm php-mysql php-mbstring php-zip php-gd php-json php-curl

# Vérifier la version PHP installée
php -v
# Exemple : PHP 8.1 → le socket sera /run/php/php8.1-fpm.sock

# Créer le lien symbolique
ln -s /usr/share/phpmyadmin /var/www/html/phpmyadmin

# Configuration Nginx pour phpMyAdmin
cat > /etc/nginx/sites-available/phpmyadmin << 'EOF'
server {
    listen 80;
    server_name 72.60.88.93;

    root /var/www/html;
    index index.php index.html;

    location /phpmyadmin {
        alias /usr/share/phpmyadmin;
        index index.php;

        location ~ \.php$ {
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $request_filename;
            # Adapter la version PHP (8.1, 8.2, 8.3...)
            fastcgi_pass unix:/run/php/php8.1-fpm.sock;
        }
    }
}
EOF

# Activer le site
ln -s /etc/nginx/sites-available/phpmyadmin /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Accès : http://72.60.88.93/phpmyadmin
```

---

## 5. Préparation du projet Django

```bash
# Créer l'utilisateur système
adduser --system --group --home /home/sav sav

# Créer le répertoire du projet
mkdir -p /home/sav/backend
chown -R sav:sav /home/sav

# ── Option A : Copier les fichiers depuis votre PC ──
# Depuis votre machine locale (PowerShell) :
# scp -r C:\Users\HP\Desktop\projets\sav-pharmacie-vite\backend\* root@72.60.88.93:/home/sav/backend/

# ── Option B : Cloner depuis Git ──
# cd /home/sav && git clone <URL_REPO> backend

# Créer l'environnement virtuel
cd /home/sav/backend
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Créer les répertoires nécessaires
mkdir -p staticfiles media logs

# Migrations et fichiers statiques
python manage.py migrate
python manage.py collectstatic --noinput

# Créer le superutilisateur
python manage.py createsuperuser

# Permissions
chown -R sav:sav /home/sav/backend
```

---

## 6. Configuration .env production

```bash
cat > /home/sav/backend/.env << 'EOF'
# ── Django ──
SECRET_KEY=GENERER_UNE_CLE_SECRETE_AVEC_50_CARACTERES_ALEATOIRES
DEBUG=False

# ── Base de données principale (Django) ──
DB_ENGINE=mysql
DB_NAME=sav_pharmacie
DB_USER=sav_user
DB_PASSWORD=MOT_DE_PASSE_FORT_ICI
DB_HOST=127.0.0.1
DB_PORT=3306

# ── Base WinDev (sync bidirectionnelle) ──
# Décommenter et remplir si le serveur WinDev MySQL est accessible
# WINDEV_DB_NAME=FacturationClient
# WINDEV_DB_USER=sav_readonly
# WINDEV_DB_PASSWORD=xxx
# WINDEV_DB_HOST=IP_SERVEUR_WINDEV
# WINDEV_DB_PORT=3306

# ── JWT ──
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# ── CORS ──
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://magicsuite.numerix.digital,https://www.magicsuite.numerix.digital

# ── Celery / Redis ──
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# ── Email (optionnel) ──
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=votre@email.com
# EMAIL_HOST_PASSWORD=mot_de_passe_app
EOF

chown sav:sav /home/sav/backend/.env
chmod 600 /home/sav/backend/.env
```

**Générer une SECRET_KEY :**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 7. Gunicorn - Serveur WSGI

```bash
# Tester que Gunicorn fonctionne
cd /home/sav/backend
source venv/bin/activate
gunicorn config.wsgi:application --bind 0.0.0.0:8001

# Créer le service systemd
cat > /etc/systemd/system/sav-gunicorn.service << 'EOF'
[Unit]
Description=SAV Pharmacie Gunicorn Daemon
After=network.target mysql.service

[Service]
User=sav
Group=sav
WorkingDirectory=/home/sav/backend
ExecStart=/home/sav/backend/venv/bin/gunicorn config.wsgi:application \
    --bind unix:/home/sav/backend/gunicorn.sock \
    --workers 3 \
    --timeout 120 \
    --access-logfile /home/sav/backend/logs/gunicorn-access.log \
    --error-logfile /home/sav/backend/logs/gunicorn-error.log
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer
systemctl daemon-reload
systemctl enable sav-gunicorn
systemctl start sav-gunicorn
systemctl status sav-gunicorn
```

---

## 8. Nginx - Reverse Proxy

```bash
cat > /etc/nginx/sites-available/api-magicsuite << 'EOF'
server {
    listen 80;
    server_name api-magicsuite.numerix.digital;

    # Redirection vers HTTPS (activée après Certbot)
    # return 301 https://$server_name$request_uri;

    client_max_body_size 10M;

    # Fichiers statiques Django
    location /static/ {
        alias /home/sav/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Fichiers médias
    location /media/ {
        alias /home/sav/backend/media/;
        expires 7d;
    }

    # Proxy vers Gunicorn
    location / {
        proxy_pass http://unix:/home/sav/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
    }
}
EOF

# Activer le site
ln -s /etc/nginx/sites-available/api-magicsuite /etc/nginx/sites-enabled/

# Supprimer le site par défaut (optionnel)
rm -f /etc/nginx/sites-enabled/default

# Tester et recharger
nginx -t
systemctl reload nginx
```

---

## 9. Certbot - SSL/HTTPS

### Prérequis DNS

Avant de lancer Certbot, assurez-vous que le **DNS est configuré** :

| Type | Nom | Valeur |
|------|-----|--------|
| A | api-magicsuite.numerix.digital | 72.60.88.93 |

Vérifier :
```bash
dig api-magicsuite.numerix.digital +short
# Doit retourner : 72.60.88.93
```

### Installation du certificat

```bash
# Obtenir le certificat SSL
certbot --nginx -d api-magicsuite.numerix.digital

# Répondre aux questions :
# → Email : votre@email.com
# → Accepter les termes : Y
# → Rediriger HTTP vers HTTPS : 2 (oui)

# Vérifier le renouvellement automatique
certbot renew --dry-run

# Le certificat se renouvelle automatiquement via un timer systemd
systemctl list-timers | grep certbot
```

### Après Certbot — Config Nginx finale (auto-modifié par Certbot)

Certbot modifiera automatiquement le fichier Nginx pour ajouter les blocs SSL. La config finale ressemblera à :

```nginx
server {
    listen 80;
    server_name api-magicsuite.numerix.digital;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api-magicsuite.numerix.digital;

    ssl_certificate /etc/letsencrypt/live/api-magicsuite.numerix.digital/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api-magicsuite.numerix.digital/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /home/sav/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/sav/backend/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://unix:/home/sav/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 10. Redis + Celery

```bash
# Redis est déjà installé (étape 2)
systemctl enable redis-server
systemctl start redis-server
redis-cli ping  # → PONG

# ── Celery Worker (service systemd) ──
cat > /etc/systemd/system/sav-celery.service << 'EOF'
[Unit]
Description=SAV Pharmacie Celery Worker
After=network.target redis-server.service

[Service]
User=sav
Group=sav
WorkingDirectory=/home/sav/backend
ExecStart=/home/sav/backend/venv/bin/celery -A config worker \
    --loglevel=info \
    --logfile=/home/sav/backend/logs/celery-worker.log \
    --concurrency=2
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# ── Celery Beat (planificateur de tâches périodiques) ──
cat > /etc/systemd/system/sav-celerybeat.service << 'EOF'
[Unit]
Description=SAV Pharmacie Celery Beat Scheduler
After=network.target redis-server.service

[Service]
User=sav
Group=sav
WorkingDirectory=/home/sav/backend
ExecStart=/home/sav/backend/venv/bin/celery -A config beat \
    --loglevel=info \
    --logfile=/home/sav/backend/logs/celery-beat.log \
    --schedule=/home/sav/backend/celerybeat-schedule
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer
systemctl daemon-reload
systemctl enable sav-celery sav-celerybeat
systemctl start sav-celery sav-celerybeat
systemctl status sav-celery sav-celerybeat
```

---

## 11. Firewall (UFW)

```bash
# Activer le firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw allow 3306/tcp    # MySQL (seulement si accès externe nécessaire)
ufw enable
ufw status
```

---

## 12. Commandes de maintenance

### Redéploiement (mise à jour du code)

```bash
cd /home/sav/backend
sudo -u sav git pull origin main      # ou scp des fichiers
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart sav-gunicorn
sudo systemctl restart sav-celery
sudo systemctl restart sav-celerybeat
```

### Vérifier les logs

```bash
# Gunicorn
tail -f /home/sav/backend/logs/gunicorn-error.log
tail -f /home/sav/backend/logs/gunicorn-access.log

# Celery
tail -f /home/sav/backend/logs/celery-worker.log
tail -f /home/sav/backend/logs/celery-beat.log

# Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Django (si configuré)
tail -f /home/sav/backend/logs/django.log
```

### Commandes utiles

```bash
# Statut de tous les services
systemctl status sav-gunicorn sav-celery sav-celerybeat nginx redis-server mysql

# Redémarrer tout
systemctl restart sav-gunicorn sav-celery sav-celerybeat nginx

# Shell Django en production
cd /home/sav/backend && source venv/bin/activate
python manage.py shell

# Renouveler manuellement le certificat SSL
certbot renew

# Vérifier l'espace disque
df -h

# Vérifier la mémoire
free -h
```

---

## Récapitulatif des URLs

| Service | URL |
|---------|-----|
| **API Django** | `https://api-magicsuite.numerix.digital/api/v1/` |
| **Swagger** | `https://api-magicsuite.numerix.digital/api/docs/` |
| **Admin Django** | `https://api-magicsuite.numerix.digital/admin/` |
| **phpMyAdmin** | `http://72.60.88.93/phpmyadmin` |

---

## Récapitulatif des services systemd

| Service | Fichier | Description |
|---------|---------|-------------|
| `sav-gunicorn` | `/etc/systemd/system/sav-gunicorn.service` | Serveur WSGI Django |
| `sav-celery` | `/etc/systemd/system/sav-celery.service` | Worker tâches async |
| `sav-celerybeat` | `/etc/systemd/system/sav-celerybeat.service` | Planificateur sync WinDev |
| `nginx` | système | Reverse proxy + SSL |
| `redis-server` | système | Broker Celery |
| `mysql` | système | Base de données |
