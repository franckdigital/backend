# SAV Pharmacie - Backend API

API Django REST Framework pour la gestion des SAV des pharmacies.  
Communication bidirectionnelle avec l'application WinDev existante.

## Architecture

```
backend/
├── config/              # Configuration Django (settings, urls, wsgi)
├── apps/
│   ├── accounts/        # Utilisateurs, auth JWT, rôles (admin/pharmacie/technicien)
│   ├── pharmacies/      # Profils pharmacies, contacts, équipements
│   ├── tickets/         # Tickets SAV, messages, pièces jointes, délégations
│   ├── zones/           # Zones géographiques, profils techniciens
│   ├── interventions/   # Rapports d'intervention avec géolocalisation
│   ├── notifications/   # Notifications email + in-app
│   ├── dashboard/       # Statistiques et exports
│   └── windev_sync/     # Synchronisation avec la base WinDev
├── media/               # Fichiers uploadés
├── static/              # Fichiers statiques
└── manage.py
```

## Installation

```bash
# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer l'environnement
copy .env.example .env
# Éditer .env avec vos paramètres

# Créer la base de données MySQL
mysql -u root -e "CREATE DATABASE sav_pharmacie CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer le superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## Endpoints API

| Préfixe | Description |
|---------|-------------|
| `/api/v1/auth/` | Authentification (login, register, JWT) |
| `/api/v1/pharmacies/` | CRUD Pharmacies |
| `/api/v1/tickets/` | CRUD Tickets SAV |
| `/api/v1/zones/` | Zones géographiques |
| `/api/v1/interventions/` | Rapports d'intervention |
| `/api/v1/notifications/` | Notifications |
| `/api/v1/dashboard/` | Statistiques et exports |
| `/api/v1/windev/` | Synchronisation WinDev |
| `/api/docs/` | **Swagger UI** |
| `/api/redoc/` | ReDoc |

## Rôles

- **Admin** : Supervision complète, CRUD tous utilisateurs, gestion zones, exports
- **Pharmacie** : Création/suivi tickets, messagerie, évaluation
- **Technicien** : Traitement tickets, rapports d'intervention, géolocalisation

## Workflow Ticket

1. Pharmacie crée un ticket
2. Attribution automatique (zone + charge + compétence)
3. Technicien accepte ou délègue
4. Intervention (en ligne ou sur site avec GPS)
5. Rapport d'intervention
6. Clôture + évaluation optionnelle

## Architecture réseau (Production)

```
┌────────────────────┐                    ┌────────────────────────┐
│    VPS Django       │                    │  Serveur WinDev        │
│    (API REST)       │◄──── MySQL 3306 ──►│  (App desktop)         │
│                     │     (réseau)       │                        │
│  Pas de BD locale   │                    │  MySQL Server          │
│  Se connecte au     │                    │  ├─ sav_pharmacie (RW) │
│  MySQL distant      │                    │  └─ FacturationCl (RO) │
└────────────────────┘                    └────────────────────────┘
```

**Les deux applications partagent le même serveur MySQL** (celui du serveur WinDev) :
- `sav_pharmacie` : base Django, lecture/écriture via user `sav_app`
- `FacturationClient` : base WinDev, lecture seule via user `sav_readonly`

### Configuration du serveur MySQL WinDev

Exécuter `sql_setup_windev_server.sql` sur le MySQL du serveur WinDev :
1. Crée la base `sav_pharmacie`
2. Crée l'utilisateur `sav_app` (RW) accessible depuis l'IP du VPS
3. Crée l'utilisateur `sav_readonly` (SELECT only) pour lire `FacturationClient`
4. Configurer `bind-address = 0.0.0.0` dans `my.cnf`
5. Ouvrir le port 3306 dans le firewall uniquement pour l'IP du VPS

### Sécurité réseau
- **Firewall** : port 3306 ouvert uniquement pour l'IP du VPS Django
- **Utilisateurs MySQL** restreints par IP source (`'user'@'IP_DU_VPS'`)
- **sav_readonly** n'a que le droit `SELECT` sur FacturationClient
- **Option recommandée** : tunnel VPN (WireGuard) entre les deux serveurs

## Synchronisation WinDev

L'API communique avec la base WinDev (FacturationClient) via :
- **`POST /api/v1/windev/sync/full/`** : Sync complète
- **`POST /api/v1/windev/sync/clients/`** : T_Client → Pharmacies
- **`POST /api/v1/windev/sync/techniciens/`** : T_Utilisateur → Techniciens
- **`POST /api/v1/windev/sync/interventions/`** : T_Intervention → Tickets
- **`POST /api/v1/windev/sync/besoins/`** : T_BesoinsClient → Tickets
- **`POST /api/v1/windev/sync/localites/`** : T_Ville/T_Localite → Zones

Configurer `WINDEV_DB_*` dans `.env` pour activer la connexion.
