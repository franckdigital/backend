#!/bin/bash
# ============================================================
# Script de déploiement - SAV Pharmacie API
# Domaine : api-magicsuite.numerix.digital
# IP : 72.60.88.93
# À exécuter en tant que root sur un serveur Ubuntu 22.04/24.04
# ============================================================

set -e  # Arrêter en cas d'erreur

# ── Variables à personnaliser ──
DOMAIN="api-magicsuite.numerix.digital"
SERVER_IP="72.60.88.93"
DB_NAME="sav_pharmacie"
DB_USER="sav_user"
DB_PASS="CHANGER_CE_MOT_DE_PASSE"
APP_USER="sav"
APP_DIR="/home/${APP_USER}/backend"
VENV_DIR="${APP_DIR}/venv"
EMAIL_CERTBOT="votre@email.com"

echo "============================================"
echo "  Déploiement SAV Pharmacie API"
echo "  Domaine : ${DOMAIN}"
echo "  IP      : ${SERVER_IP}"
echo "============================================"

# ──────────────────────────────────────────
# 1. MISE À JOUR SYSTÈME
# ──────────────────────────────────────────
echo "[1/11] Mise à jour du système..."
apt update && apt upgrade -y

# ──────────────────────────────────────────
# 2. INSTALLATION DES PAQUETS
# ──────────────────────────────────────────
echo "[2/11] Installation des paquets..."
apt install -y \
  python3 python3-pip python3-venv python3-dev \
  build-essential libmysqlclient-dev pkg-config \
  nginx certbot python3-certbot-nginx \
  git curl wget unzip supervisor \
  redis-server \
  mysql-server mysql-client \
  php-fpm php-mysql php-mbstring php-zip php-gd php-json php-curl

# ──────────────────────────────────────────
# 3. CONFIGURATION MYSQL
# ──────────────────────────────────────────
echo "[3/11] Configuration MySQL..."
systemctl enable mysql
systemctl start mysql

mysql -u root << MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

echo "  → Base ${DB_NAME} et utilisateur ${DB_USER} créés."

# ──────────────────────────────────────────
# 4. INSTALLATION PHPMYADMIN
# ──────────────────────────────────────────
echo "[4/11] Installation phpMyAdmin..."
if [ ! -d /usr/share/phpmyadmin ]; then
  DEBIAN_FRONTEND=noninteractive apt install -y phpmyadmin
fi
ln -sf /usr/share/phpmyadmin /var/www/html/phpmyadmin

# Détection version PHP
PHP_VERSION=$(php -r "echo PHP_MAJOR_VERSION.'.'.PHP_MINOR_VERSION;")
PHP_SOCK="/run/php/php${PHP_VERSION}-fpm.sock"

cat > /etc/nginx/sites-available/phpmyadmin << NGINX_PMA
server {
    listen 80;
    server_name ${SERVER_IP};

    root /var/www/html;
    index index.php index.html;

    location /phpmyadmin {
        alias /usr/share/phpmyadmin;
        index index.php;

        location ~ \.php\$ {
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME \$request_filename;
            fastcgi_pass unix:${PHP_SOCK};
        }
    }
}
NGINX_PMA

ln -sf /etc/nginx/sites-available/phpmyadmin /etc/nginx/sites-enabled/
echo "  → phpMyAdmin configuré sur http://${SERVER_IP}/phpmyadmin"

# ──────────────────────────────────────────
# 5. UTILISATEUR ET PROJET DJANGO
# ──────────────────────────────────────────
echo "[5/11] Préparation du projet Django..."
id ${APP_USER} &>/dev/null || adduser --system --group --home /home/${APP_USER} ${APP_USER}
mkdir -p ${APP_DIR}

# IMPORTANT : Copier les fichiers du projet dans ${APP_DIR} avant de continuer
# scp -r backend/* root@${SERVER_IP}:${APP_DIR}/
if [ ! -f "${APP_DIR}/manage.py" ]; then
  echo "  ⚠ ATTENTION : Copiez les fichiers du projet dans ${APP_DIR} puis relancez ce script."
  echo "  Depuis votre PC : scp -r backend/* root@${SERVER_IP}:${APP_DIR}/"
  exit 1
fi

# Environnement virtuel
python3 -m venv ${VENV_DIR}
${VENV_DIR}/bin/pip install --upgrade pip
${VENV_DIR}/bin/pip install -r ${APP_DIR}/requirements.txt
${VENV_DIR}/bin/pip install gunicorn

# Répertoires
mkdir -p ${APP_DIR}/staticfiles ${APP_DIR}/media ${APP_DIR}/logs

# ──────────────────────────────────────────
# 6. FICHIER .env
# ──────────────────────────────────────────
echo "[6/11] Création du fichier .env..."
SECRET_KEY=$(${VENV_DIR}/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

cat > ${APP_DIR}/.env << ENVFILE
SECRET_KEY=${SECRET_KEY}
DEBUG=False

DB_ENGINE=mysql
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASS}
DB_HOST=127.0.0.1
DB_PORT=3306

# WinDev sync (décommenter si serveur WinDev accessible)
# WINDEV_DB_NAME=FacturationClient
# WINDEV_DB_USER=sav_readonly
# WINDEV_DB_PASSWORD=xxx
# WINDEV_DB_HOST=IP_SERVEUR_WINDEV
# WINDEV_DB_PORT=3306

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://magicsuite.numerix.digital,https://www.magicsuite.numerix.digital

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
ENVFILE

chown ${APP_USER}:${APP_USER} ${APP_DIR}/.env
chmod 600 ${APP_DIR}/.env
echo "  → .env créé avec SECRET_KEY générée."

# ──────────────────────────────────────────
# 7. MIGRATIONS ET STATIC
# ──────────────────────────────────────────
echo "[7/11] Migrations et collectstatic..."
cd ${APP_DIR}
${VENV_DIR}/bin/python manage.py migrate --noinput
${VENV_DIR}/bin/python manage.py collectstatic --noinput
chown -R ${APP_USER}:${APP_USER} ${APP_DIR}

# ──────────────────────────────────────────
# 8. SERVICE GUNICORN
# ──────────────────────────────────────────
echo "[8/11] Configuration Gunicorn..."
cat > /etc/systemd/system/sav-gunicorn.service << 'GUNICORN_SVC'
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
GUNICORN_SVC

systemctl daemon-reload
systemctl enable sav-gunicorn
systemctl start sav-gunicorn

# ──────────────────────────────────────────
# 9. CONFIGURATION NGINX
# ──────────────────────────────────────────
echo "[9/11] Configuration Nginx..."
cat > /etc/nginx/sites-available/api-magicsuite << 'NGINX_API'
server {
    listen 80;
    server_name api-magicsuite.numerix.digital;

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
        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
    }
}
NGINX_API

ln -sf /etc/nginx/sites-available/api-magicsuite /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# ──────────────────────────────────────────
# 10. CERTBOT SSL
# ──────────────────────────────────────────
echo "[10/11] Configuration SSL avec Certbot..."
echo "  → Assurez-vous que le DNS A record pointe ${DOMAIN} → ${SERVER_IP}"
echo "  → Vérification : dig ${DOMAIN} +short"

certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos -m ${EMAIL_CERTBOT} --redirect

echo "  → Certificat SSL installé."
certbot renew --dry-run

# ──────────────────────────────────────────
# 11. REDIS + CELERY
# ──────────────────────────────────────────
echo "[11/11] Configuration Redis et Celery..."
systemctl enable redis-server
systemctl start redis-server

cat > /etc/systemd/system/sav-celery.service << 'CELERY_SVC'
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
CELERY_SVC

cat > /etc/systemd/system/sav-celerybeat.service << 'BEAT_SVC'
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
BEAT_SVC

systemctl daemon-reload
systemctl enable sav-celery sav-celerybeat
systemctl start sav-celery sav-celerybeat

# ──────────────────────────────────────────
# FIREWALL
# ──────────────────────────────────────────
echo "Configuration du firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# ──────────────────────────────────────────
# RÉSUMÉ
# ──────────────────────────────────────────
echo ""
echo "============================================"
echo "  DÉPLOIEMENT TERMINÉ !"
echo "============================================"
echo ""
echo "  API Django  : https://${DOMAIN}/api/v1/"
echo "  Swagger     : https://${DOMAIN}/api/docs/"
echo "  Admin       : https://${DOMAIN}/admin/"
echo "  phpMyAdmin  : http://${SERVER_IP}/phpmyadmin"
echo ""
echo "  Services systemd :"
echo "    - sav-gunicorn   (Gunicorn)"
echo "    - sav-celery     (Celery Worker)"
echo "    - sav-celerybeat (Celery Beat)"
echo ""
echo "  Logs : ${APP_DIR}/logs/"
echo ""
echo "  ⚠ N'oubliez pas :"
echo "    1. Créer le superutilisateur : cd ${APP_DIR} && source venv/bin/activate && python manage.py createsuperuser"
echo "    2. Modifier DB_PASS dans .env si vous avez changé le mot de passe MySQL"
echo "    3. Configurer la connexion WinDev dans .env si nécessaire"
echo "============================================"
