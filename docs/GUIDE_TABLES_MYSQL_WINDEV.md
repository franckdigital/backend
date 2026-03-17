# Guide : Création des tables MySQL côté WinDev pour la synchronisation avec Django

## 1. Vue d'ensemble

L'application Django se connecte à la base MySQL `FacturationClient` gérée par WinDev pour :
- **LIRE** les données métier (clients, techniciens, interventions, localités)
- **ÉCRIRE** les tickets SAV et rapports d'intervention créés depuis l'interface web

Ce document décrit comment créer et maintenir les tables MySQL côté WinDev pour que la synchronisation bidirectionnelle fonctionne correctement.

---

## 2. Prérequis

| Élément | Requis |
|---|---|
| MySQL Server | 8.0+ (recommandé 8.4) |
| Moteur de stockage | InnoDB (obligatoire) |
| Charset | utf8mb4 |
| Collation | utf8mb4_unicode_ci |
| Accès natif WinDev | Accès natif MySQL activé dans WinDev |

---

## 3. Création de la base de données

```sql
CREATE DATABASE IF NOT EXISTS FacturationClient
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE FacturationClient;
```

---

## 4. Tables lues par Django (WinDev → Django)

Ces tables sont **gérées par WinDev**. Django les lit toutes les 2 minutes pour importer les données.

### 4.1 T_Client (Pharmacies / Clients)

> ⚠️ **Cette table existe déjà dans votre base WinDev.** Les colonnes ci-dessous sont celles du schéma réel généré par WinDev.

**Colonnes utilisées par Django (SELECT) :**
| Colonne | Type réel | Usage Django |
|---|---|---|
| `IDClient` | BIGINT PK AUTO_INCREMENT | Lien `Pharmacie.windev_client_id` |
| `NomClient` | VARCHAR(100) | Nom de la pharmacie |
| `TelFixe` | VARCHAR(30) | Téléphone fixe |
| `TelCel` | VARCHAR(30) | Téléphone cellulaire |
| `telCel2` | VARCHAR(20) | Téléphone secondaire |
| `Code_2ST` | VARCHAR(10) | Code unique pharmacie |
| `AdresseGeo` | VARCHAR(50) | Adresse géographique |
| `EmailClient` | VARCHAR(50) | Email de contact |
| `NomResponsable` | VARCHAR(50) | Nom du pharmacien responsable |
| `TelPharmacien` | VARCHAR(15) | Téléphone du pharmacien |
| `SousContrat` | TINYINT | 0 = non, 1 = sous contrat SAV |
| `IDLocalite` | BIGINT FK | Lien vers T_Localite (commune) |
| `ActifOP` | TINYINT | 0 = inactif, 1 = actif |
| `InterieurPays` | TINYINT | 0 = Abidjan, 1 = intérieur |
| `DateMaintenance` | DATE | Date de dernière maintenance |
| `MontantContrat` | INTEGER | Montant du contrat |
| `DateDernierModif` | DATE | Détecte les modifications (sync incrémentale) |

### 4.2 T_Utilisateur (Techniciens / Utilisateurs)

> ⚠️ **Table existante WinDev.** Django lit uniquement les techniciens.

**Colonnes utilisées par Django (SELECT) :**
| Colonne | Type réel | Usage Django |
|---|---|---|
| `IDUtilisateur` | BIGINT PK AUTO_INCREMENT | Lien `User.windev_user_id` |
| `CodeUtilisateur` | VARCHAR(20) UNIQUE | Utilisé comme `username` Django |
| `NomComplet` | VARCHAR(50) | Nom complet du technicien |
| `TelCel` | VARCHAR(30) | Téléphone principal |
| `telCel2` | VARCHAR(20) | Téléphone secondaire |
| `ActifOP` | TINYINT | 0 = inactif, 1 = actif |
| `Technicien` | TINYINT | 0 = non technicien, 1 = technicien |
| `Disponible` | TINYINT | Disponibilité du technicien |
| `IDProfil` | VARCHAR(20) FK | Profil utilisateur WinDev |
| `DateDernierModif` | DATE | Sync incrémentale |

**Filtrage Django :** `WHERE Technicien = 1 AND (IDUtilisateur > last_id OR DateDernierModif >= last_sync)`

### 4.3 T_Intervention

> ⚠️ **Table existante WinDev.** Colonnes réelles du schéma.

**Colonnes utilisées par Django (SELECT) :**
| Colonne | Type réel | Usage Django |
|---|---|---|
| `IDIntervention` | BIGINT PK AUTO_INCREMENT | Lien `Ticket.windev_intervention_id` |
| `DateIntervention` | DATE | Date de l'intervention |
| `IDClient` | BIGINT FK T_Client | Lien vers la pharmacie |
| `IDTypeIntervention` | VARCHAR(20) FK T_TypeIntervention | Type (Dépannage, Inventaire, etc.) |
| `IDUtilisateur` | BIGINT FK T_Utilisateur | 1er technicien assigné |
| `IDIntervention2emeUtilisateur` | BIGINT | 2ème technicien (optionnel) |
| `ValideOP` | TINYINT | 0 = non validée, 1 = validée |
| `AnnuleOP` | TINYINT | 0 = active, 1 = annulée |
| `EffectueOP` | TINYINT | 0 = non effectuée, 1 = effectuée |
| `NbJours` | INTEGER | Nombre de jours d'intervention |
| `DateChoisie` | DATE | Date choisie début |
| `DateChoisieFin` | DATE | Date choisie fin |
| `MontantTTC` | INTEGER | Montant facturé TTC |
| `Frais_Technicien` | INTEGER | Frais technicien |
| `DateAjout` | TIMESTAMP | Date de création |
| `DateDernierModif` | TIMESTAMP | Dernière modification |

**Filtrage Django :** `WHERE AnnuleOP = 0 AND IDIntervention > last_synced_id`

### 4.3b T_TypeIntervention (référentiel)

| Colonne | Type | Valeurs observées |
|---|---|---|
| `IDTypeIntervention` | VARCHAR(20) PK | DEPANNAGE, MIXTE, INVENTAIRE, MAINTENANCE, MAJ |
| `LibTypeIntervention` | VARCHAR(50) | Libellé du type |

### 4.4 T_Ville (Régions / Villes)

| Colonne | Type réel | Usage Django |
|---|---|---|
| `IDVille` | BIGINT PK AUTO_INCREMENT | Code région `WD-{IDVille}` |
| `NomVille` | VARCHAR(50) UNIQUE | Nom de la ville → `Region.name` |

### 4.5 T_Localite (Communes / Localités)

| Colonne | Type réel | Usage Django |
|---|---|---|
| `IDLocalite` | BIGINT PK AUTO_INCREMENT | Code commune `WD-{IDLocalite}` |
| `NomLocalite` | VARCHAR(50) | Nom localité → `Commune.name` |
| `IDVille` | BIGINT FK T_Ville | Lien vers la ville/région |

---

## 5. Tables écrites par Django (Django → WinDev)

Ces tables **existent déjà** dans votre base WinDev. Django y insère et met à jour des données. Les enregistrements créés par Django sont identifiés par le préfixe `[SAV Web]` dans les champs description.

### 5.1 T_BesoinsClient (Besoins clients / Tickets SAV)

> ⚠️ **Table existante WinDev.** Schéma réel ci-dessous. Django INSERT + UPDATE.

**Colonnes réelles du schéma WinDev :**
| Colonne | Type réel | Django écrit ? | Usage |
|---|---|---|---|
| `IDBesoinsClient` | BIGINT PK AUTO_INCREMENT | Non (auto) | ID unique |
| `DateBesoin` | DATE | ✅ INSERT | Date de la demande |
| `DateAjout` | TIMESTAMP | ✅ INSERT (NOW()) | Date de création |
| `HeureEnreg` | TIME | Non | Heure d'enregistrement |
| `DescriptionBesoin` | LONGTEXT | ✅ INSERT | Description préfixée `[SAV Web]` |
| `ValideOP` | TINYINT | ✅ INSERT + UPDATE | 0 = non validé, 1 = validé |
| `Traite` | TINYINT | ✅ INSERT + UPDATE | 0 = non traité, 1 = traité |
| `Annule` | TINYINT | ✅ INSERT (toujours 0) | 0 = actif |
| `NomTechnicien` | VARCHAR(50) | ✅ INSERT + UPDATE | Nom du technicien assigné |
| `IDClient` | BIGINT FK T_Client | ✅ INSERT | Lien vers la pharmacie |
| `IDUtilisateur` | INTEGER | ✅ INSERT | IDUtilisateur WinDev du technicien |
| `IDUtilisateur_Validation` | INTEGER | Non | Rempli par WinDev |
| `IDUtilisateur_Traitement` | INTEGER | Non | Rempli par WinDev |
| `IDUtilisateur_Annulation` | INTEGER | Non | Rempli par WinDev |
| `DateDernierModif` | TIMESTAMP | ✅ UPDATE (NOW()) | Dernière modification |

**Comment distinguer les données Django des données WinDev :**
- Django préfixe `DescriptionBesoin` avec `[SAV Web]`
- WinDev ne met pas de préfixe

**Mapping statuts Django → colonnes WinDev :**
| Statut Django | ValideOP | Traite |
|---|---|---|
| nouveau | 0 | 0 |
| assigné / en_cours | 1 | 0 |
| résolu / clôturé | 1 | 1 |

### 5.2 T_DetailIntervention (Détails d'intervention)

> ⚠️ **Table existante WinDev.** Django INSERT uniquement.

**Colonnes réelles du schéma WinDev :**
| Colonne | Type réel | Django écrit ? | Usage |
|---|---|---|---|
| `IDDetailIntervention` | BIGINT PK AUTO_INCREMENT | Non (auto) | ID unique |
| `IDIntervention` | BIGINT FK T_Intervention | ✅ INSERT | Lien vers l'intervention |
| `IDNature` | BIGINT FK T_Nature | ✅ INSERT (0 par défaut) | Nature de l'intervention |
| `DescriptionDetail` | LONGTEXT | ✅ INSERT | Description préfixée `[SAV Web]` |
| `IDUtilisateur` | BIGINT | ✅ INSERT | IDUtilisateur du technicien |
| `DateAjout` | TIMESTAMP | ✅ INSERT (NOW()) | Date de création |
| `DateDernierModif` | TIMESTAMP | ✅ INSERT (NOW()) | Dernière modification |

**Contenu de `DescriptionDetail` écrit par Django :**
```
[SAV Web] Actions réalisées par le technicien
Résultat: Résolu / Partiellement résolu / Non résolu
Temps: XX min
Recommandations: ...
```

---

## 6. Utilisateur MySQL pour Django

Django se connecte avec un utilisateur MySQL dédié qui a des droits restreints :

```sql
-- Créer l'utilisateur de synchronisation
CREATE USER IF NOT EXISTS 'sav_sync'@'IP_DU_VPS_DJANGO'
    IDENTIFIED BY 'mot_de_passe_fort';

-- Lecture sur TOUTES les tables
GRANT SELECT ON FacturationClient.* TO 'sav_sync'@'IP_DU_VPS_DJANGO';

-- Écriture UNIQUEMENT sur les tables de sync
GRANT INSERT, UPDATE ON FacturationClient.T_Client
    TO 'sav_sync'@'IP_DU_VPS_DJANGO';
GRANT INSERT, UPDATE ON FacturationClient.T_BesoinsClient
    TO 'sav_sync'@'IP_DU_VPS_DJANGO';
GRANT INSERT, UPDATE ON FacturationClient.T_DetailIntervention
    TO 'sav_sync'@'IP_DU_VPS_DJANGO';

FLUSH PRIVILEGES;
```

> ⚠️ Remplacer `IP_DU_VPS_DJANGO` par l'adresse IP réelle du serveur VPS.

---

## 7. Règles anti-conflit (TRÈS IMPORTANT)

### 7.1 Règle de propriété par préfixe

```
┌──────────────────────────────────────────────────────────┐
│  RÈGLE D'OR : Ne jamais modifier ce qui ne t'appartient  │
│                                                          │
│  WinDev ne modifie PAS les lignes dont Description       │
│  commence par [SAV Web] (créées par Django)              │
│  Django ne modifie PAS les lignes créées par WinDev      │
│  (celles sans préfixe [SAV Web])                         │
└──────────────────────────────────────────────────────────┘
```

### 7.2 Pas de suppression physique

```
INTERDIT : DELETE FROM T_Client WHERE IDClient = 42;
CORRECT  : UPDATE T_Client SET ActifOP = 0 WHERE IDClient = 42;

INTERDIT : DELETE FROM T_Intervention WHERE IDIntervention = 10;
CORRECT  : UPDATE T_Intervention SET AnnuleOP = 1 WHERE IDIntervention = 10;
```

### 7.3 Pas de reset d'AUTO_INCREMENT

```
-- ⛔ JAMAIS faire ça :
ALTER TABLE T_Client AUTO_INCREMENT = 1;
TRUNCATE TABLE T_Client;

-- Django utilise les IDs pour la sync incrémentale.
-- Si les IDs reculent, des données seront ignorées.
```

### 7.4 Toujours mettre à jour DateDernierModif

Si WinDev modifie un enregistrement, la colonne `DateDernierModif` doit être mise à jour. Avec `ON UPDATE CURRENT_TIMESTAMP`, c'est automatique pour les UPDATE SQL. Mais si WinDev utilise les fonctions HyperFile :

```
// WinDev : après modification d'un client
T_Client.NomClient = "Nouveau nom"
T_Client.DateDernierModif = DateHeureSys()  // ← Obligatoire !
HModifie(T_Client)
```

---

## 8. Code WinDev : Connexion MySQL

### 8.1 Initialisation de la connexion

```
// Projet WinDev → Code d'initialisation du projet
gsConnexionMySQL est une Connexion

gsConnexionMySQL.Fournisseur    = hAccèsNatifMySQL
gsConnexionMySQL.Serveur        = "127.0.0.1"
gsConnexionMySQL.Utilisateur    = "root"
gsConnexionMySQL.MotDePasse     = "votre_mot_de_passe"
gsConnexionMySQL.BaseDeDonnées  = "FacturationClient"
gsConnexionMySQL.AccèsNatif    = hAccèsNatifMySQL

SI PAS HOuvreConnexion(gsConnexionMySQL) ALORS
    Erreur("Connexion MySQL impossible : " + HErreurInfo())
    FinProgramme()
FIN

// Associer les fichiers de données à la connexion MySQL
HChangeConnexion(T_Client, gsConnexionMySQL)
HChangeConnexion(T_Utilisateur, gsConnexionMySQL)
HChangeConnexion(T_Intervention, gsConnexionMySQL)
HChangeConnexion(T_BesoinsClient, gsConnexionMySQL)
HChangeConnexion(T_DetailIntervention, gsConnexionMySQL)
HChangeConnexion(T_Ville, gsConnexionMySQL)
HChangeConnexion(T_Localite, gsConnexionMySQL)
```

### 8.2 Création des tables depuis WinDev

```
// Créer les tables si elles n'existent pas
// (Alternative au SQL direct : WinDev peut créer les tables)
HCréationSiInexistant(T_Client)
HCréationSiInexistant(T_Utilisateur)
HCréationSiInexistant(T_Intervention)
HCréationSiInexistant(T_BesoinsClient)
HCréationSiInexistant(T_DetailIntervention)
HCréationSiInexistant(T_Ville)
HCréationSiInexistant(T_Localite)
```

### 8.3 Écriture d'un besoin depuis WinDev

```
// Ajouter un besoin client depuis WinDev
T_BesoinsClient.IDClient          = nIDClient
T_BesoinsClient.DateBesoin        = DateDuJour()
T_BesoinsClient.DescriptionBesoin = "Problème écran caisse"
T_BesoinsClient.ValideOP          = 0
T_BesoinsClient.Traite            = 0
T_BesoinsClient.Annule            = 0
T_BesoinsClient.IDUtilisateur     = gnIDUtilisateurCourant
HAjoute(T_BesoinsClient)

// Lire les besoins créés par Django (pour affichage)
HExécuteRequêteSQL(REQ_BesoinsWeb, gsConnexionMySQL, ...
    "SELECT * FROM T_BesoinsClient WHERE DescriptionBesoin LIKE '[SAV Web]%' ORDER BY DateAjout DESC")
```

### 8.4 Ne PAS modifier les données Django

```
// ⚠️ Avant de modifier un besoin, vérifier s'il vient de Django :
HLitRecherchePremier(T_BesoinsClient, IDBesoinsClient, nIDBesoin)
SI PAS HEnDehors() ALORS
    SI Gauche(T_BesoinsClient.DescriptionBesoin, 9) = "[SAV Web]" ALORS
        // ⛔ Ne pas modifier — créé par Django
        Info("Ce besoin provient de l'application web. Modification interdite.")
        RETOUR
    FIN
    // ✅ OK, c'est un besoin WinDev — on peut modifier
    T_BesoinsClient.ValideOP = 1
    T_BesoinsClient.DateDernierModif = DateHeureSys()
    HModifie(T_BesoinsClient)
FIN
```

---

## 9. Schéma récapitulatif

```
┌──────────────────────────────────────────────────────────────────────┐
│                    BASE MySQL : FacturationClient                    │
│                                                                      │
│  Tables WinDev (WinDev = propriétaire principal)                     │
│  ┌─────────────────┐ ┌──────────────────┐ ┌────────────────────┐    │
│  │   T_Client       │ │  T_Utilisateur   │ │  T_Intervention    │    │
│  │   (pharmacies)   │ │  (techniciens)   │ │  (interventions)   │    │
│  │ WinDev+Django RW │ │  WinDev W/Dj R   │ │  WinDev W/Dj R     │    │
│  └────────┬────────┘ └────────┬─────────┘ └────────┬───────────┘    │
│           │                   │                     │                │
│           │      WinDev ÉCRIT + Django LIT/ÉCRIT    │                │
│           ▼                   ▼                     ▼                │
│  ┌─────────────────┐ ┌──────────────────┐                           │
│  │   T_Ville        │ │  T_Localite      │                           │
│  │   (régions)      │ │  (communes)      │                           │
│  └─────────────────┘ └──────────────────┘                           │
│                                                                      │
│  Tables partagées (WinDev + Django écrivent)                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  T_BesoinsClient                                              │   │
│  │  Django préfixe DescriptionBesoin avec [SAV Web]              │   │
│  │  WinDev utilise ValideOP/Traite/Annule pour le statut         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  T_DetailIntervention                                         │   │
│  │  Django préfixe DescriptionDetail avec [SAV Web]              │   │
│  │  WinDev utilise IDNature pour la nature de l'intervention     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

         ▲ SELECT (lecture)              ▲ SELECT + INSERT/UPDATE
         │                               │ (sur T_BesoinsClient et
         │                               │  T_DetailIntervention)
         │                               │
    ┌────┴──────┐                  ┌─────┴──────┐
    │  WinDev   │                  │   Django    │
    │  Desktop  │                  │   (VPS)     │
    └───────────┘                  └────────────┘
```

---

## 10. Checklist avant mise en production

- [ ] MySQL Server installé et démarré sur le serveur WinDev
- [ ] Base `FacturationClient` créée en utf8mb4
- [ ] Tables existent dans FacturationClient (T_Client, T_Utilisateur, T_Intervention, T_BesoinsClient, T_DetailIntervention, T_Ville, T_Localite, T_TypeIntervention, T_Nature)
- [ ] Colonne `DateDernierModif` présente sur T_Client, T_Utilisateur, T_BesoinsClient
- [ ] Utilisateur MySQL `sav_sync` créé avec droits restreints (SELECT sur tout, INSERT/UPDATE sur T_BesoinsClient et T_DetailIntervention uniquement)
- [ ] Port 3306 ouvert dans le firewall pour l'IP du VPS Django
- [ ] WinDev connecté à MySQL via accès natif (`HChangeConnexion`)
- [ ] WinDev ne modifie PAS les enregistrements dont la description commence par `[SAV Web]`
- [ ] Pas de DELETE physique, uniquement `ActifOP = 0` / `AnnuleOP = 1`
- [ ] Pas de TRUNCATE ou reset d'AUTO_INCREMENT
- [ ] Données de test insérées pour valider la première synchronisation
