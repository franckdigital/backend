# Guide de Synchronisation — Explication pour le Client

## Comment l'application web SAV communique avec votre système WinDev

---

## En résumé

Votre application WinDev (MagicSuite) et notre application web SAV **partagent la même base de données MySQL** (`FacturationClient`). Les deux systèmes fonctionnent en parallèle, chacun lit et écrit dans cette base. La synchronisation est **automatique** et **transparente** — aucune action manuelle n'est nécessaire.

```
  ┌──────────────────────────┐          ┌──────────────────────────┐
  │    APPLICATION WINDEV     │          │    APPLICATION WEB SAV    │
  │    (MagicSuite)           │          │    (Django + React)       │
  │                           │          │                           │
  │  - Gestion des clients    │          │  - Portail pharmacies     │
  │  - Interventions          │          │  - Tickets SAV            │
  │  - Inventaires            │          │  - Rapports terrain       │
  │  - Facturation            │          │  - Tableau de bord        │
  │  - Prospects              │          │  - Application mobile     │
  └───────────┬───────────────┘          └──────────┬────────────────┘
              │                                      │
              │         BASE DE DONNÉES MYSQL         │
              │      ┌──────────────────────┐        │
              └─────►│  FacturationClient   │◄───────┘
                     │  (serveur MySQL)      │
                     └──────────────────────┘
```

**Les deux applications coexistent. L'une ne remplace pas l'autre.**

---

## Ce qui est synchronisé

### Sens 1 : WinDev → Application Web (lecture)

L'application web **lit** les données créées par WinDev pour les afficher aux pharmacies et techniciens.

| Donnée WinDev | Table MySQL | Ce que l'app web en fait |
|---|---|---|
| **Clients (pharmacies)** | `T_Client` | Affiche la liste des pharmacies, crée un compte web pour chaque pharmacie |
| **Techniciens** | `T_Utilisateur` | Affiche la liste des techniciens disponibles pour l'assignation des tickets |
| **Interventions** | `T_Intervention` | Affiche l'historique des interventions passées aux pharmacies |
| **Villes et localités** | `T_Ville`, `T_Localite` | Utilisées pour le découpage géographique (zones) |

> Quand vous ajoutez un nouveau client ou technicien dans WinDev, il apparaît automatiquement dans l'application web.

### Sens 2 : Application Web → WinDev (écriture)

L'application web **écrit** dans la base MySQL pour que WinDev puisse voir les données créées en ligne.

| Donnée Web | Table MySQL | Ce que WinDev voit |
|---|---|---|
| **Tickets SAV** | `T_BesoinsClient` | Les demandes SAV créées par les pharmacies en ligne apparaissent comme des "besoins client" |
| **Rapports d'intervention** | `T_DetailIntervention` | Les rapports rédigés par les techniciens sur le terrain |
| **Statuts des tickets** | `T_BesoinsClient` | Quand un ticket est résolu/clôturé, le champ "Traité" est mis à jour |
| **Nouvelles pharmacies** | `T_Client` | Les pharmacies créées via le web sont ajoutées dans la table clients |

> Quand une pharmacie crée un ticket SAV sur le portail web, ce ticket apparaît dans WinDev comme un "besoin client" dans `T_BesoinsClient`.

---

## Comment fonctionne la synchronisation

### Fréquence

| Mode | Fréquence | Déclenchement |
|---|---|---|
| **Automatique** | Toutes les **2 minutes** | Le serveur Django exécute la sync en arrière-plan |
| **Manuelle** | À la demande | Un administrateur clique sur le bouton "Synchroniser" dans le tableau de bord |
| **Bidirectionnelle** | À la demande | Exécute les deux sens en une seule opération |

### Processus détaillé

```
  Toutes les 2 minutes :

  1. LECTURE (WinDev → Web)
     ├── Lire les nouveaux clients dans T_Client         → Créer/mettre à jour les pharmacies
     ├── Lire les nouveaux techniciens dans T_Utilisateur → Créer/mettre à jour les techniciens
     └── Lire les nouvelles interventions dans T_Intervention → Mettre à jour l'historique

  2. ÉCRITURE (Web → WinDev)
     ├── Écrire les nouveaux tickets dans T_BesoinsClient     → Visibles dans WinDev
     ├── Écrire les rapports dans T_DetailIntervention         → Visibles dans WinDev
     ├── Mettre à jour les statuts dans T_BesoinsClient        → "Traité" quand résolu
     └── Écrire les nouvelles pharmacies dans T_Client         → Visibles dans WinDev
```

### Incrémentale (pas de doublons)

La synchronisation est **incrémentale** : elle ne traite que les enregistrements **nouveaux ou modifiés** depuis le dernier cycle. Chaque entité a un "curseur" qui mémorise le dernier ID traité.

Exemple :
- Dernier client synchronisé : ID 45
- Au prochain cycle, seuls les clients avec ID > 45 sont traités
- Pas de risque de doublons, pas de rechargement complet

---

## Ce que WinDev doit faire (ou pas)

### Aucune modification de WinDev n'est nécessaire

L'application web se connecte **directement** à la base MySQL `FacturationClient`. WinDev n'a rien à changer dans son code. La synchronisation est entièrement gérée côté Django.

### Prérequis techniques (déjà en place)

| Prérequis | Statut | Détail |
|---|---|---|
| Base MySQL accessible | ✅ | `FacturationClient` sur le serveur MySQL |
| Utilisateur MySQL dédié | ✅ | `sav_sync` avec droits limités |
| Port 3306 ouvert | ✅ | Accessible depuis le serveur Django |
| Tables existantes | ✅ | `T_Client`, `T_Utilisateur`, `T_Intervention`, `T_BesoinsClient`, `T_DetailIntervention` |

### Droits de l'utilisateur MySQL `sav_sync`

| Table | Droits | Explication |
|---|---|---|
| `T_Client` | SELECT, INSERT, UPDATE | Lire les clients + écrire les nouvelles pharmacies web |
| `T_Utilisateur` | SELECT | Lire les techniciens (lecture seule) |
| `T_Intervention` | SELECT | Lire les interventions (lecture seule) |
| `T_Ville` | SELECT | Lire les villes (lecture seule) |
| `T_Localite` | SELECT | Lire les localités (lecture seule) |
| `T_BesoinsClient` | SELECT, INSERT, UPDATE | Lire + écrire les besoins/tickets |
| `T_DetailIntervention` | SELECT, INSERT, UPDATE | Lire + écrire les détails d'intervention |

> **Important** : L'utilisateur `sav_sync` **ne peut PAS supprimer** (pas de DELETE) ni modifier la structure des tables. Vos données existantes sont protégées.

---

## Sécurité

### Protection des données WinDev

| Mesure | Description |
|---|---|
| **Pas de DELETE** | Django ne peut jamais supprimer de données dans `FacturationClient` |
| **Écriture limitée** | Django n'écrit que dans `T_BesoinsClient`, `T_DetailIntervention` et `T_Client` |
| **Utilisateur dédié** | `sav_sync` a des droits minimaux (principe du moindre privilège) |
| **Pas de modification de structure** | Django ne peut pas ALTER/DROP les tables |
| **Connexion locale** | En production : connexion via réseau privé, pas via internet |
| **Logs** | Chaque synchronisation est journalisée (date, nombre d'enregistrements, erreurs) |

### Séparation des responsabilités

```
  WINDEV est maître de :                L'APPLICATION WEB est maître de :
  ─────────────────────                 ──────────────────────────────────
  - Clients existants                   - Tickets SAV (créés par les pharmacies)
  - Interventions                       - Rapports terrain (par les techniciens)
  - Inventaires                         - Messages et évaluations
  - Facturation                         - Notifications
  - Prospects                           - Zones géographiques
  - Congés                              - Statistiques / Dashboard
```

---

## Que se passe-t-il en cas de problème ?

### Le serveur web est en panne

| Composant | Impact |
|---|---|
| **WinDev** | **Aucun impact.** WinDev continue de fonctionner normalement. |
| **Sync** | Suspendue. Reprend automatiquement au redémarrage du serveur Django. |
| **Données** | Aucune perte. Les données créées pendant la panne seront synchronisées au prochain cycle. |

### La connexion internet est coupée

| Composant | Impact |
|---|---|
| **WinDev** | **Aucun impact.** WinDev fonctionne en local. |
| **Application web** | Temporairement inaccessible pour les pharmacies/techniciens. |
| **Sync** | Suspendue. La sync incrémentale rattrape le retard automatiquement au retour d'internet. |

### La base MySQL est redémarrée

| Composant | Impact |
|---|---|
| **WinDev** | Redémarrage normal. |
| **Sync** | Reprend au prochain cycle (2 minutes max). |
| **Données** | Aucune perte grâce à la sync incrémentale. |

---

## Interface d'administration de la synchronisation

L'administrateur dispose d'une page dédiée dans le tableau de bord web pour surveiller la synchronisation :

### Boutons d'action

| Bouton | Action |
|---|---|
| **WinDev → Django** | Importe les dernières données de WinDev vers l'application web |
| **Django → WinDev** | Exporte les tickets et rapports vers WinDev |
| **Sync complète** | Exécute les deux sens en une seule opération |

### Informations affichées

| Information | Description |
|---|---|
| **Curseurs de synchronisation** | Dernier ID synchronisé par entité (client, technicien, etc.) |
| **Historique des synchronisations** | Date, heure, nombre d'enregistrements, statut (succès/erreur) |
| **État de la connexion MySQL** | Connecté / Déconnecté |
| **Nombre de clients WinDev** | Total des pharmacies dans `T_Client` |

---

## En production : ce qui change

### Configuration réseau

```
  Aujourd'hui (développement local) :
  ────────────────────────────────────
  Django ──► localhost:3306 ──► MySQL local

  En production (chez le client) :
  ────────────────────────────────
  Serveur Django (VPS)  ──► IP_SERVEUR_WINDEV:3306 ──► MySQL WinDev
```

### Ce qu'il faut configurer chez le client

1. **Ouvrir le port 3306** du serveur MySQL WinDev pour l'IP du VPS Django
2. **Créer l'utilisateur MySQL** `sav_sync` avec les droits listés ci-dessus
3. **Mettre à jour le fichier `.env`** du serveur Django :

```env
WINDEV_DB_HOST=<IP_DU_SERVEUR_MYSQL_WINDEV>
WINDEV_DB_PORT=3306
WINDEV_DB_NAME=FacturationClient
WINDEV_DB_USER=sav_sync
WINDEV_DB_PASSWORD=<mot_de_passe_sécurisé>
```

4. **Tester la connexion** depuis le VPS :
```bash
mysql -h <IP_SERVEUR_WINDEV> -u sav_sync -p FacturationClient
```

5. **Lancer la première synchronisation** depuis le tableau de bord admin

---

## Comment WinDev se connecte à MySQL (double connexion HyperFileSQL + MySQL)

### Architecture de stockage WinDev

WinDev utilise **deux systèmes de base de données en parallèle** :

```
APPLICATION WINDEV (MagicSuite)
├── HyperFileSQL (HFSQL)
│   ├── Base locale embarquée dans l'application
│   ├── Utilisée pour les données internes WinDev
│   ├── Fichiers .fic / .ndx / .mmo sur le disque local
│   └── Accès ultra-rapide, pas besoin de serveur
│
└── MySQL (FacturationClient)
    ├── Base externe sur un serveur MySQL
    ├── Utilisée pour les données partagées (clients, interventions, etc.)
    ├── Accessible par WinDev ET par Django simultanément
    └── C'est cette base que Django synchronise
```

### Pourquoi deux bases ?

| Base | Usage | Avantage |
|---|---|---|
| **HyperFileSQL** | Données internes WinDev (configuration, préférences, cache local) | Rapide, pas de serveur nécessaire, embarqué |
| **MySQL** | Données métier partagées (clients, interventions, facturation) | Accessible par plusieurs applications simultanément |

> L'application web Django ne se connecte **qu'à MySQL** (`FacturationClient`). Elle n'a pas accès aux données HyperFileSQL et n'en a pas besoin.

### Script de connexion WinDev → MySQL

Voici le code WLangage utilisé dans WinDev pour se connecter à la base MySQL `FacturationClient` :

```wlanguage
// ─── Déclaration de la connexion MySQL ───
MaConnexionMySQL est une Connexion

// Paramètres de connexion
MaConnexionMySQL.Provider     = hAccèsNatifMySQL
MaConnexionMySQL.Serveur      = "127.0.0.1"        // IP du serveur MySQL
MaConnexionMySQL.Port         = 3306                // Port MySQL (par défaut 3306)
MaConnexionMySQL.Utilisateur  = "root"              // Utilisateur MySQL
MaConnexionMySQL.MotDePasse   = "mot_de_passe"      // Mot de passe MySQL
MaConnexionMySQL.BaseDeDonnées = "FacturationClient" // Nom de la base

// Ouverture de la connexion
SI PAS HOuvreConnexion(MaConnexionMySQL) ALORS
    Erreur("Impossible de se connecter à MySQL", HErreurInfo())
    RETOUR
FIN

Info("Connexion MySQL établie avec succès !")
```

### Script alternatif avec HChangeConnexion (méthode courante)

```wlanguage
// ─── Connexion MySQL via HChangeConnexion ───
// Cette méthode redirige les fichiers de données WinDev vers MySQL

// 1. Déclarer la connexion
gnConnexion est une Connexion
gnConnexion.Provider       = hAccèsNatifMySQL
gnConnexion.Serveur        = gsServeurMySQL    // Variable globale : IP du serveur
gnConnexion.Port           = 3306
gnConnexion.Utilisateur    = gsUserMySQL       // Variable globale : utilisateur
gnConnexion.MotDePasse     = gsMDPMySQL        // Variable globale : mot de passe
gnConnexion.BaseDeDonnées  = "FacturationClient"

// 2. Ouvrir la connexion
SI PAS HOuvreConnexion(gnConnexion) ALORS
    Erreur("Échec connexion MySQL : " + HErreurInfo())
    RETOUR
FIN

// 3. Rediriger les fichiers de données vers MySQL
// Chaque fichier WinDev (ex: T_Client) est redirigé vers la table MySQL
HChangeConnexion(T_Client, gnConnexion)
HChangeConnexion(T_Utilisateur, gnConnexion)
HChangeConnexion(T_Intervention, gnConnexion)
HChangeConnexion(T_BesoinsClient, gnConnexion)
HChangeConnexion(T_DetailIntervention, gnConnexion)
HChangeConnexion(T_Ville, gnConnexion)
HChangeConnexion(T_Localite, gnConnexion)
HChangeConnexion(T_TypeIntervention, gnConnexion)
```

### Comment les deux systèmes cohabitent

```
WINDEV (MagicSuite)
│
├── Données locales (HyperFileSQL)
│   └── HLitPremier(FichierLocal)    // Accès direct fichier .fic
│
├── Données partagées (MySQL via HChangeConnexion)
│   ├── HLitPremier(T_Client)        // Redirigé vers MySQL
│   ├── HAjoute(T_Client)            // INSERT dans MySQL
│   └── HModifie(T_Client)           // UPDATE dans MySQL
│
└── Les fonctions H* (HLitPremier, HAjoute, etc.) fonctionnent
    de la même façon que ce soit HFSQL ou MySQL.
    WinDev abstrait la connexion : le code ne change pas.

DJANGO (Application Web)
│
└── Se connecte directement à MySQL via le connecteur Python mysqlclient
    ├── Lit T_Client, T_Utilisateur, etc. (sync WinDev → Django)
    └── Écrit dans T_BesoinsClient, T_Client, etc. (sync Django → WinDev)
```

### Point clé : accès simultané

Les deux applications (WinDev et Django) accèdent à la **même base MySQL** en même temps :
- **WinDev** lit et écrit dans `FacturationClient` via le connecteur natif MySQL
- **Django** lit et écrit dans `FacturationClient` via le connecteur Python `mysqlclient`
- **MySQL gère les accès concurrents** automatiquement (transactions, verrous)
- Il n'y a **aucun conflit** car chaque application a ses propres tables prioritaires

---

## Processus de synchronisation et création des utilisateurs

### Les utilisateurs sont créés PENDANT la synchronisation

Il n'y a pas de "avant" ou "après" — la création des comptes utilisateurs Django fait **partie intégrante** du processus de synchronisation. Quand la sync lit un client ou technicien dans WinDev, elle crée automatiquement le compte Django correspondant.

### Ordre d'exécution de `run_full_sync()`

```
1. run_windev_referentials()           → T_Ville, T_Localite → Region, Commune
2. run_windev_to_django()              → dans cet ordre :
   a. sync_clients_incremental()       → T_Client → User (pharmacie) + Pharmacie
   b. sync_techniciens_incremental()   → T_Utilisateur → User (technicien) + TechnicienProfile
   c. sync_interventions_incremental() → T_Intervention → Ticket
   d. sync_besoins_incremental()       → T_BesoinsClient → Ticket
3. run_django_to_windev()              → sens inverse
```

> **L'ordre est important** : les référentiels (villes/localités) sont synchronisés en premier, puis les utilisateurs (clients/techniciens), et enfin les tickets. Les tickets ont besoin des utilisateurs et pharmacies déjà créés pour les associer correctement.

### Détail étape par étape pour un client (pharmacie)

`sync_clients_incremental()` :

1. Lit `T_Client` dans la base WinDev (tous les clients avec `IDClient > dernier_sync` ou `DateDernierModif >= dernière_date`)
2. **Pour chaque client WinDev** :
   - **Crée un `User` Django** avec :
     - `username` = `pharma_wd_{IDClient}` (ex : `pharma_wd_7`, `pharma_wd_9`)
     - `role` = `pharmacie`
     - `password` = `sav_{IDClient}_temp` (ex : `sav_7_temp`)
     - `is_validated` = `True`
   - **Crée/met à jour une `Pharmacie`** liée à ce user avec les infos WinDev (nom, adresse, téléphone, email, etc.)

### Détail pour un technicien

`sync_techniciens_incremental()` :

1. Lit `T_Utilisateur WHERE Technicien = 1` dans WinDev
2. **Pour chaque technicien WinDev** :
   - **Crée un `User` Django** avec :
     - `username` = `CodeUtilisateur` ou `tech_wd_{IDUtilisateur}`
     - `role` = `technicien`
     - `password` = `tech_{IDUtilisateur}_temp`
   - **Crée un `TechnicienProfile`** lié

### Ensuite seulement, les tickets

`sync_interventions_incremental()` et `sync_besoins_incremental()` cherchent les `Pharmacie` et `User` **déjà créés aux étapes précédentes** pour lier les tickets aux bons utilisateurs et pharmacies.

### Schéma visuel du flux complet

```
BASE WINDEV (FacturationClient)          BASE DJANGO (sav_pharmacie)
─────────────────────────────           ──────────────────────────

T_Ville / T_Localite ──────────────→ Region / Commune
        ↓ (étape 1)

T_Client ──────────────────────────→ User (role=pharmacie) + Pharmacie
        ↓ (étape 2a)                    username: pharma_wd_7
                                        password: sav_7_temp

T_Utilisateur (Technicien=1) ──────→ User (role=technicien) + TechnicienProfile
        ↓ (étape 2b)                    username: TECH05
                                        password: tech_3_temp

T_Intervention ────────────────────→ Ticket (lié à Pharmacie + User technicien)
        ↓ (étape 2c)                    ↑ dépend des users créés au-dessus

T_BesoinsClient ───────────────────→ Ticket
        (étape 2d)
```

### Points importants sur les mots de passe

| Point | Détail |
|---|---|
| **Mots de passe temporaires** | `sav_{IDClient}_temp` (pharmacies) et `tech_{IDUtilisateur}_temp` (techniciens) |
| **Définis une seule fois** | Le mot de passe est défini uniquement à la **première création** (`if created:`) — les syncs suivantes ne l'écrasent pas |
| **Modification par l'admin** | L'administrateur peut modifier le mot de passe d'un utilisateur via l'interface web (endpoint `set_password`) |
| **Connexion au système** | Pour les anciens clients WinDev, l'admin doit définir un mot de passe personnalisé avant de leur donner accès au portail Django |

---

## Résumé pour le client

| Question | Réponse |
|---|---|
| Faut-il modifier WinDev ? | **Non.** Aucune modification du code WinDev. |
| Faut-il modifier la base de données ? | **Non.** On utilise les tables existantes. Il faut juste créer un utilisateur MySQL. |
| Y a-t-il un risque pour les données existantes ? | **Non.** Django ne peut ni supprimer ni modifier la structure. Écriture limitée à 3 tables. |
| La sync est-elle automatique ? | **Oui.** Toutes les 2 minutes, sans intervention. |
| Que se passe-t-il si le serveur web tombe ? | **WinDev continue normalement.** La sync reprend automatiquement au redémarrage. |
| Les pharmacies voient-elles les données des autres ? | **Non.** Chaque pharmacie ne voit que ses propres données. |
| Combien coûte le fonctionnement ? | **~15-25 €/mois** pour le serveur VPS. Pas de licence logicielle. |

---

*Document préparé par l'équipe de développement SAV Pharmacie — Mars 2026*
