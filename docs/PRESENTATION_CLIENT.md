# SAV Pharmacie — Solution de Gestion du Service Après-Vente

## Présentation de la solution digitale pour le suivi et la gestion des interventions techniques

---

## Le constat

Aujourd'hui, la gestion du SAV repose sur une application WinDev installée localement sur vos serveurs. Cette application fonctionne bien pour les opérations quotidiennes, mais présente des **limitations** :

| Limitation actuelle | Impact |
|---|---|
| Accessible uniquement en local | Les pharmacies et techniciens sur le terrain n'ont pas accès |
| Pas de suivi en temps réel | Les pharmacies ne savent pas où en est leur demande |
| Communication par téléphone/email | Perte d'information, pas de traçabilité |
| Pas de rapports d'intervention digitaux | Rapports papier, difficiles à retrouver |
| Pas de tableau de bord | Pas de vision globale de l'activité SAV |
| Pas d'application mobile | Les techniciens doivent revenir au bureau pour saisir |

---

## Notre solution

Une **application web et mobile moderne** qui se connecte à votre système WinDev existant, **sans le remplacer**.

```
    Votre système actuel            +         Notre solution
    ─────────────────────                     ────────────────

    Application WinDev                        Application Web (Admin)
    (gestion interne)                         (tableau de bord, suivi)
         │                                          │
         │                                    Application Mobile
         │                                    (techniciens + pharmacies)
         │                                          │
         └──────────── MySQL ───────────────────────┘
                   (synchronisation automatique
                     toutes les 2 minutes)
```

### Ce que nous NE faisons PAS
- Nous ne remplaçons PAS votre application WinDev
- Nous ne modifions PAS vos processus internes
- Nous ne touchons PAS à vos données existantes

### Ce que nous AJOUTONS
- Un **portail web** pour le suivi des interventions
- Une **application mobile** pour les techniciens et les pharmacies
- Une **synchronisation automatique** entre les deux systèmes
- Des **tableaux de bord** et des **statistiques** en temps réel

---

## Les bénéfices concrets

### Pour vos clients (les pharmacies)

| Avant | Après |
|---|---|
| Appelle pour signaler un problème | Crée un ticket en ligne en 30 secondes |
| Attend sans savoir l'état | Suit l'avancement en temps réel |
| Relance par téléphone | Reçoit des notifications automatiques |
| Pas de trace écrite | Historique complet des interventions |
| Ne sait pas quel technicien vient | Voit le technicien assigné et l'heure prévue |

**Résultat** : Satisfaction client améliorée, moins d'appels téléphoniques, transparence totale.

### Pour vos techniciens

| Avant | Après |
|---|---|
| Reçoit les missions par téléphone | Voit ses missions sur son téléphone |
| Rédige un rapport papier | Remplit le rapport sur l'application mobile |
| Revient au bureau pour saisir | Tout est synchronisé automatiquement |
| Pas de géolocalisation | Navigation GPS vers la pharmacie |
| Pas de photos | Peut joindre des photos au rapport |

**Résultat** : Gain de temps, moins d'erreurs, plus de missions par jour.

### Pour votre gestion (direction/admin)

| Avant | Après |
|---|---|
| Pas de vue d'ensemble | Tableau de bord en temps réel |
| Statistiques manuelles (Excel) | Rapports automatiques |
| Difficile de mesurer la performance | KPIs : délais, taux de résolution, charge |
| Planification manuelle | Attribution intelligente des techniciens |
| Pas d'historique facilement accessible | Recherche et filtres avancés |

**Résultat** : Meilleure visibilité, décisions basées sur les données, optimisation des ressources.

---

## Comparaison : Application actuelle (WebDev) vs Notre solution (Django + React)

> Application actuelle : **http://magicsuite.ddns.net/suiviclient**
> Titre : *"Gestion des Interventions et Inventaires"*
> Technologie : WebDev (PC SOFT) — Éditeur : **SARL MagicSuite**

### Inventaire complet de l'application WebDev actuelle

L'application actuelle se compose de **3 modules** accessibles depuis la page d'accueil :

**Module 1 — Gestion des Interventions (menu orange) :**
| Écran | Ce qu'il fait |
|---|---|
| Nouvelle intervention | Formulaire : client, type (Inventaire/Dépannage/Mixte/Maintenance/MAJ), 2 techniciens, dates proposées/choisies, montant facturé, frais, tâches avec descriptions |
| Liste interventions | Tableau filtrable par dates, type, technicien, client, frais. Colonnes : Nom client, N°, Type, Techniciens, Nb jours, Dates, Montant TTC, Frais, Validé, Effectué |
| Interventions à valider | Workflow de validation des interventions |
| Planning interventions | Vue calendrier par date avec filtre type intervention |
| Congés et permissions | Liste des absences : agent, dates, heures, motif |
| Point inventaire | Suivi des inventaires pharmacies |
| Point frais d'intervention | Suivi financier des frais techniciens |

**Module 2 — Paramètres Standards (menu jaune) :**
| Écran | Ce qu'il fait |
|---|---|
| Clients | Liste complète : Nom, Solde, Code, Contrat, Intérieur, Localité, Téléphones, Responsable, Adresse, Email. Filtres : Tous/Intérieur, Sous contrat/Sans contrat, Actif/Inactif, Avec solde, Par ville. 30+ clients (pharmacies). Accès à distance disponible |
| Prospects | Suivi commercial : Nom, Responsable, Téléphone, Localité, Email, Logiciel actuel, Date logiciel, Option recherchée. Filtres : Magic présenté, Déjà contacté, RDV effectué, Intérieur, À rappeler, RDV pris, Devenu client |
| Localités | Liste par ville (Abidjan, Soubré, Bingerville...) avec codes. Localités : Abobo, Adjamé, Cocody, Plateau, Port-Bouet... |
| Villes | Référentiel des villes |
| Réindexer BD | Outil de maintenance base de données |

**Module 3 — Paramètres Avancés (menu vert) :**
| Écran | Ce qu'il fait |
|---|---|
| Modes paiements | Carte bancaire, Chèque, Espèce, MoovMoney, MTN Money, Orange Money, OrangeMoney, Virement, Wave |
| Types interventions | Dépannage, Mixte, Inventaire, Maintenance, MAJ |
| Natures interventions | Dépannage logiciel, Dépannage matériel, Dépannage réseau, Inventaire, Maintenance périodique, Mise à jour MagicSuite |
| Utilisateurs | Gestion des comptes utilisateurs |
| Profils | Gestion des profils/rôles |
| Requêtes | Requêtes personnalisées sur les données |

### Comparaison générale

| Critère | Application WebDev (MagicSuite) | Notre solution (Django + React) |
|---|---|---|
| **Technologie** | WebDev (PC SOFT) — pages AWP serveur | Django REST API + React SPA + React Native |
| **Architecture** | Monolithique (tout sur un serveur) | API séparée du frontend (scalable) |
| **Hébergement** | Serveur local (magicsuite.ddns.net) | VPS professionnel + domaine dédié |
| **Protocole** | ⚠️ HTTP non sécurisé ("Non sécurisé" dans Chrome) | HTTPS obligatoire (SSL/TLS, cadenas vert) |
| **URL** | DNS dynamique ddns.net | Domaine professionnel (.com / .ci) |
| **Application mobile** | Aucune (web desktop uniquement) | React Native (iOS + Android) |
| **API REST** | Non disponible | Oui, documentation Swagger automatique |
| **Navigation** | Rechargement complet à chaque clic (bouton "Retour") | SPA : navigation instantanée sans rechargement |
| **Responsive** | Non (interface fixe desktop) | 100% responsive, mobile-first |

### Interface utilisateur (UI/UX)

| Critère | WebDev (MagicSuite) | Django + React |
|---|---|---|
| **Design** | Interface années 2000 (icônes clipart, fonds dégradés bleu/jaune/vert, watermark MagicSuite) | Interface moderne (TailwindCSS, composants shadcn/ui) |
| **Page d'accueil** | Grille d'icônes clipart par catégorie | Dashboard avec KPIs, graphiques, activité récente |
| **Formulaires** | Champs HTML basiques, boutons "Valider/Nouveau/Retour" | Formulaires validés en temps réel, auto-complétion, stepper |
| **Tableaux** | Tableaux colorés (fond cyan/jaune), colonnes tronquées, pas de pagination | Tableaux triables, filtrables, paginés, exportables (Excel/PDF) |
| **Filtres** | Boutons radio (Tous/Un), champs date manuels | Filtres combinés en temps réel, recherche instantanée |
| **Impression** | Boutons "Imprimer prévues"/"Imprimer réalisées" (impression navigateur) | Export PDF stylisé, envoi par email |
| **Thème** | Fixe (bleu/blanc avec watermark) | Mode clair/sombre, personnalisable |
| **Notifications** | Aucune | Push + in-app en temps réel |
| **Filigrane** | Logo MagicSuite répété en arrière-plan | Aucun (interface propre) |

### Sécurité

| Critère | WebDev (MagicSuite) | Django + React |
|---|---|---|
| **Protocole** | ⚠️ HTTP — Chrome affiche "Non sécurisé" | HTTPS (chiffrement SSL/TLS) |
| **Login** | Login + Mot de passe + Confirmation mot de passe (formulaire basique) | JWT (tokens avec expiration automatique) |
| **Données en transit** | En clair (mot de passe visible par interception réseau) | Chiffrées de bout en bout |
| **Gestion des rôles** | Profils et utilisateurs (basique) | 3 rôles (Admin, Pharmacie, Technicien) + permissions granulaires par action |
| **Session** | Session serveur WebDev (AWP) | Tokens JWT stateless + refresh token |
| **Audit** | Non visible | Historique complet de chaque action (qui, quand, quoi) |
| **Protection** | Aucune protection visible (pas de CORS, pas de rate limiting) | Rate limiting, CORS, validation, anti-CSRF |

### Comparaison fonctionnalité par fonctionnalité

#### Gestion des interventions

| Fonctionnalité | WebDev (MagicSuite) | Django + React |
|---|---|---|
| **Créer une intervention** | ✅ Formulaire avec client, type, 2 techniciens, dates proposées/choisies, montant, frais | ✅ Formulaire enrichi + pièces jointes, photos, catégorie, urgence |
| **Liste des interventions** | ✅ Tableau filtrable (dates, type, technicien, client, frais) | ✅ Tableau avancé + recherche instantanée + export Excel/PDF |
| **Planning** | ⚠️ Vue calendrier basique (une seule ligne par date, vide) | ✅ Planning interactif avec drag & drop, vue jour/semaine/mois |
| **Validation** | ✅ Écran "Interventions à valider" | ✅ Workflow de validation avec notifications automatiques |
| **Frais d'intervention** | ✅ Suivi montant TTC + frais techniciens | ✅ Suivi financier + graphiques de tendance |
| **Inventaires** | ✅ Liste complète (pharmacie, dates, techniciens, montants HT/TTC, frais société/technicien) | ⬜ Reste dans WinDev (synchronisé en lecture) |
| **2 techniciens par intervention** | ✅ 1er et 2ème technicien | ✅ Technicien principal + possibilité de délégation |
| **Tâches détaillées** | ✅ Tableau "Détail intervention" (tâche + description) | ✅ Rapport structuré : diagnostic, actions, pièces, recommandations |
| **Rapports d'intervention** | ❌ Pas de rapport terrain | ✅ Saisie mobile avec photos, GPS, signature numérique |

#### Gestion des clients / pharmacies

| Fonctionnalité | WebDev (MagicSuite) | Django + React |
|---|---|---|
| **Liste clients** | ✅ 30+ pharmacies avec solde, code, contrat, téléphones, responsable, email, adresse, localité | ✅ Liste enrichie + carte géographique + historique interventions |
| **Filtres** | ✅ Tous/Intérieur, Sous contrat/Sans contrat, Actif/Inactif, Avec solde, Par ville | ✅ Mêmes filtres + recherche par nom/code + filtres combinés |
| **Accès à distance** | ✅ Bouton "accès à distance" | ✅ Accès depuis n'importe quel appareil (web + mobile) |
| **Création de client** | ✅ Bouton "Nouveau" | ✅ Formulaire complet avec géolocalisation automatique |
| **Solde client** | ✅ Colonne "Solde" | ⬜ Reste dans WinDev (données financières) |
| **Contrat** | ✅ Checkbox "contrat" + filtre | ✅ Champ "sous contrat" + date contrat + alerte expiration |
| **Accès par le client** | ❌ Seuls les admins accèdent | ✅ **NOUVEAU** : chaque pharmacie a son propre accès pour créer des tickets |

#### Gestion des prospects (commercial)

| Fonctionnalité | WebDev (MagicSuite) | Django + React |
|---|---|---|
| **Liste prospects** | ✅ Avec filtres : Magic présenté, Déjà contacté, RDV effectué, Intérieur, À rappeler, RDV pris, Devenu client | ⬜ Non prévu (reste dans WinDev — fonctionnalité commerciale) |
| **Suivi commercial** | ✅ Logiciel actuel, Date logiciel, Option recherchée | ⬜ Hors périmètre SAV |

#### Paramétrage

| Fonctionnalité | WebDev (MagicSuite) | Django + React |
|---|---|---|
| **Types d'interventions** | ✅ Dépannage, Mixte, Inventaire, Maintenance, MAJ | ✅ Catégories : Logiciel, Matériel, Réseau, Autre |
| **Natures d'interventions** | ✅ Dépannage logiciel/matériel/réseau, Inventaire, Maintenance, MAJ MagicSuite | ✅ Types : Assistance en ligne, Intervention sur site |
| **Modes de paiement** | ✅ Carte, Chèque, Espèce, MoovMoney, MTN Money, Orange Money, Virement, Wave | ⬜ Hors périmètre (pas de facturation dans Django) |
| **Localités** | ✅ Villes + localités (Abidjan → Abobo, Cocody, Plateau...) | ✅ Synchronisé depuis WinDev → Régions + Communes + Quartiers |
| **Utilisateurs / Profils** | ✅ Gestion basique | ✅ 3 rôles + permissions granulaires + validation de compte |
| **Requêtes personnalisées** | ✅ Module requêtes | ✅ API REST + filtres avancés + export |
| **Congés / Permissions** | ✅ Agent, dates, heures, motif | ⬜ Non prévu (reste dans WinDev — RH) |

#### Ce que notre solution AJOUTE (n'existe pas dans WebDev)

| Fonctionnalité nouvelle | Description |
|---|---|
| **Tickets SAV par les pharmacies** | Les pharmacies créent elles-mêmes leurs demandes (plus besoin d'appeler) |
| **Application mobile** | iOS + Android pour techniciens et pharmacies |
| **Suivi en temps réel** | Statut du ticket visible à tout moment par la pharmacie |
| **Notifications automatiques** | Push + in-app quand un ticket est créé, assigné, résolu |
| **Messagerie par ticket** | Échanges pharmacie ↔ technicien tracés et archivés |
| **Rapports terrain enrichis** | Photos, géolocalisation GPS, signature numérique, durée |
| **Évaluation du service** | Note 1-5 + commentaire par la pharmacie après résolution |
| **Dashboard statistiques** | KPIs, temps moyen de résolution, charge techniciens, tendances |
| **Gestion des zones** | Affectation des techniciens par zone géographique |
| **Délégation de tickets** | Transfert entre techniciens avec motif et traçabilité |
| **Historique complet** | Chaque changement de statut, assignation, message est tracé |
| **HTTPS sécurisé** | Données chiffrées (contrairement au HTTP actuel) |
| **API REST documentée** | Permet des intégrations futures (ERP, BI, autres apps) |

### Performance et scalabilité

| Critère | WebDev (MagicSuite) | Django + React |
|---|---|---|
| **Architecture** | Serveur unique monolithique (AWP) | API + Frontend séparés (scalable) |
| **Utilisateurs simultanés** | Limité par le serveur WebDev | Scalable (Gunicorn multi-workers) |
| **Temps de réponse** | Rechargement complet de page à chaque clic | Réponses API < 100ms, navigation SPA instantanée |
| **Cache** | Aucun côté client | Cache Redis côté serveur |
| **Disponibilité** | Serveur local + DNS dynamique (ddns.net) | VPS 99.9% uptime + monitoring |
| **Maintenance** | Nécessite accès physique au serveur | Déploiement à distance, mise à jour sans interruption |
| **Backups** | Manuels | Automatiques quotidiens |

### Ce que l'application actuelle fait bien

L'application WebDev MagicSuite a des **points forts** qu'il faut reconnaître :

- ✅ **Gestion complète des interventions** — création, validation, planning, suivi financier
- ✅ **Gestion des inventaires** — avec calcul des frais société/technicien
- ✅ **Base clients riche** — solde, contrat, intérieur/extérieur, accès à distance
- ✅ **Gestion des prospects** — suivi commercial complet
- ✅ **Paramétrage fin** — types/natures d'interventions, modes de paiement (Mobile Money)
- ✅ **Congés et permissions** — gestion RH des techniciens
- ✅ **Accessible depuis un navigateur** — pas d'installation côté client
- ✅ **Données centralisées** — base MySQL

**Notre approche ne remplace pas ces fonctionnalités.** Elle les **complète** en ajoutant tout ce qui manque côté client (pharmacies) et terrain (techniciens) : accès mobile, tickets SAV, suivi en temps réel, notifications, rapports terrain, statistiques, et sécurité HTTPS.

### Résumé visuel : ce qui existe vs ce que nous ajoutons

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   APPLICATION ACTUELLE (WebDev)           NOTRE SOLUTION (Django + React)  │
│   magicsuite.ddns.net/suiviclient         domaine-professionnel.ci         │
│                                                                             │
│   ✅ Interventions (création, liste,      ✅ Interventions (enrichies +     │
│      validation, planning, frais)            photos, GPS, signature)        │
│   ✅ Inventaires (pharmacies)             ✅ Tickets SAV (NOUVEAU)          │
│   ✅ Clients (30+ pharmacies)             ✅ Accès pharmacie (NOUVEAU)      │
│   ✅ Prospects (suivi commercial)         ✅ App mobile iOS/Android         │
│   ✅ Congés / Permissions                 ✅ Suivi temps réel               │
│   ✅ Modes de paiement (Mobile Money)     ✅ Notifications push             │
│   ✅ Types/Natures interventions          ✅ Dashboard + statistiques       │
│   ✅ Localités/Villes                     ✅ Messagerie par ticket          │
│                                           ✅ Évaluation client              │
│   ❌ Pas de mobile                        ✅ Zones géographiques            │
│   ❌ Pas de tickets SAV                   ✅ API REST documentée            │
│   ❌ Pas de notifications                 ✅ HTTPS sécurisé                 │
│   ❌ HTTP non sécurisé                    ✅ Export PDF / Excel             │
│   ❌ DNS dynamique                                                          │
│   ❌ Pas de dashboard                                                       │
│   ❌ Pas d'accès pharmacie                                                  │
│                                                                             │
│          Les deux coexistent et se synchronisent                            │
│                 automatiquement toutes les 2 minutes                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Comment ça marche techniquement

### La synchronisation automatique

```
┌─────────────────────────┐                    ┌─────────────────────────┐
│   APPLICATION WINDEV     │                    │   APPLICATION WEB/MOBILE│
│   (votre système actuel) │                    │   (notre solution)      │
│                          │                    │                         │
│   Gestion des clients    │───── toutes ──────►│   Voit les clients      │
│   Gestion des techniciens│── les 2 min ──────►│   Voit les techniciens  │
│   Gestion des interv.    │───────────────────►│   Voit les interventions│
│                          │                    │                         │
│   Voit les tickets web   │◄──────────────────│   Crée des tickets SAV  │
│   Voit les rapports web  │◄── toutes ────────│   Rédige des rapports   │
│                          │◄── les 2 min ─────│   Met à jour les statuts│
└─────────────────────────┘                    └─────────────────────────┘
```

- **Délai de synchronisation : 2 minutes maximum**
- **Bidirectionnelle** : ce qui est fait dans WinDev est visible sur le web, et inversement
- **Automatique** : aucune intervention humaine nécessaire
- **Sécurisée** : connexions chiffrées, accès restreints par IP, utilisateurs MySQL dédiés

### Aucune interruption de votre activité

La solution fonctionne **en parallèle** de votre système WinDev :

1. **Votre équipe interne** continue d'utiliser WinDev normalement
2. **Les pharmacies** utilisent le portail web ou l'app mobile pour créer des tickets
3. **Les techniciens** utilisent l'app mobile sur le terrain
4. **Les deux systèmes** sont synchronisés automatiquement toutes les 2 minutes

> Aucune migration, aucun changement d'habitude pour votre équipe WinDev.

---

## Les fonctionnalités principales

### 1. Gestion des tickets SAV

- Création de tickets par les pharmacies (web/mobile)
- Attribution automatique ou manuelle aux techniciens
- Suivi d'état : Nouveau → En cours → Résolu → Clôturé
- Priorités : Basse, Normale, Haute, Urgente
- Pièces jointes (photos, documents)
- Historique complet de chaque ticket

### 2. Rapports d'intervention

- Saisie sur le terrain via l'application mobile
- Diagnostic, actions effectuées, pièces utilisées
- Recommandations pour le client
- Durée de l'intervention
- Signature du client (optionnel)
- Synchronisé automatiquement vers WinDev

### 3. Tableau de bord en temps réel

- Nombre de tickets ouverts / en cours / résolus
- Temps moyen de résolution
- Performance par technicien
- Répartition géographique des interventions
- Tendances sur la semaine / le mois

### 4. Gestion des zones géographiques

- Découpage par régions et communes
- Attribution des techniciens par zone
- Visualisation sur carte

### 5. Notifications

- Notification au technicien quand un ticket lui est assigné
- Notification à la pharmacie quand le ticket est pris en charge
- Notification quand l'intervention est terminée
- Rappels automatiques pour les tickets en retard

### 6. Application mobile

- Interface optimisée pour smartphone
- Fonctionne en 3G/4G/WiFi
- Navigation GPS vers les pharmacies
- Saisie rapide des rapports d'intervention
- Mode hors-ligne (synchronisation au retour du réseau)

---

## Sécurité des données

| Mesure | Détail |
|---|---|
| **Accès restreint par IP** | Seul le serveur Django peut accéder au MySQL WinDev |
| **Utilisateurs MySQL dédiés** | Droits limités : Django ne peut écrire que dans 2 tables spécifiques |
| **Pas de suppression** | Django ne peut PAS supprimer de données dans votre base WinDev |
| **Authentification JWT** | Tokens sécurisés avec expiration pour l'API |
| **HTTPS obligatoire** | Toutes les communications web sont chiffrées |
| **Pare-feu** | Port 3306 ouvert uniquement pour l'IP du serveur Django |
| **Séparation des données** | Les données web et WinDev sont identifiées par une colonne "source" |
| **Sauvegarde** | Sauvegarde automatique quotidienne des bases de données |

> **Vos données WinDev sont protégées** : Django a des droits de lecture sur toute la base, mais ne peut écrire que dans les tables de synchronisation (tickets et rapports créés depuis le web).

---

## Stack technique

| Composant | Technologie | Pourquoi |
|---|---|---|
| **Backend API** | Django 4.2 + DRF | Framework Python robuste, sécurisé, rapide à développer |
| **Base de données** | MySQL 8.x | Compatible avec WinDev, performant, fiable |
| **Frontend Web** | React + Vite | Interface moderne, rapide, responsive |
| **Application Mobile** | React Native | Une seule base de code pour iOS + Android |
| **Synchronisation** | Celery + Redis | Tâches asynchrones, planification automatique |
| **Serveur Web** | Nginx + Gunicorn | Standard industrie pour les applications Python |
| **Hébergement** | VPS Linux | Stable, évolutif, coût maîtrisé |

---

## Planning de déploiement

| Phase | Durée | Contenu |
|---|---|---|
| **Phase 1** — Configuration | 1-2 jours | Installation MySQL côté WinDev, création des tables, configuration réseau |
| **Phase 2** — Déploiement Django | 1 jour | Mise en place du VPS, déploiement de l'API, tests de connexion |
| **Phase 3** — Sync initiale | 1 jour | Première synchronisation, vérification des données, ajustements |
| **Phase 4** — Formation | 1-2 jours | Formation de l'équipe admin, des pharmacies pilotes, des techniciens |
| **Phase 5** — Mise en production | 1 jour | Passage en production, monitoring, support initial |
| **Phase 6** — Suivi | Continu | Corrections, améliorations, support |

**Durée totale estimée : 1 à 2 semaines** pour une mise en production complète.

---

## Coût de fonctionnement

| Poste | Coût estimé / mois |
|---|---|
| VPS Django (2 vCPU, 4 Go RAM) | 10 - 20 € |
| Nom de domaine | 1 € |
| Certificat SSL | Gratuit (Let's Encrypt) |
| Stockage fichiers (photos, docs) | Inclus dans le VPS |
| **Total** | **~15 - 25 € / mois** |

> Pas de licence logicielle, pas de coût par utilisateur, pas de frais cachés.
> Le coût se limite à l'hébergement du serveur.

---

## Pourquoi cette approche est la bonne

### 1. Pas de remplacement de l'existant
Votre équipe continue d'utiliser WinDev. Aucune formation lourde, aucune migration risquée.

### 2. Synchronisation automatique
Les données circulent dans les deux sens, toutes les 2 minutes, sans intervention humaine.

### 3. Accessible partout
Les pharmacies et techniciens accèdent à l'application depuis n'importe quel appareil connecté à internet.

### 4. Évolutif
La solution peut grandir avec vos besoins : nouveaux modules, plus d'utilisateurs, intégrations supplémentaires.

### 5. Sécurisé
Accès restreints, données chiffrées, séparation des responsabilités entre WinDev et Django.

### 6. Coût maîtrisé
Infrastructure légère, pas de licence, coût mensuel prévisible.

---

## Questions fréquentes

**Q : Est-ce que ça va ralentir notre application WinDev ?**
> Non. Django lit la base MySQL avec des requêtes optimisées et légères. L'impact sur les performances est négligeable.

**Q : Que se passe-t-il si le VPS tombe en panne ?**
> Votre application WinDev continue de fonctionner normalement. La synchronisation reprendra automatiquement dès que le VPS sera rétabli.

**Q : Que se passe-t-il si internet est coupé ?**
> WinDev fonctionne en local, pas d'impact. L'application web sera temporairement inaccessible. Dès le retour d'internet, la synchronisation rattrape le retard automatiquement.

**Q : Les pharmacies auront-elles accès aux données confidentielles ?**
> Non. Chaque pharmacie ne voit que ses propres tickets et interventions. Les données des autres clients sont invisibles.

**Q : Peut-on ajouter d'autres fonctionnalités plus tard ?**
> Oui. L'architecture est modulaire. On peut ajouter : facturation, gestion de stock, planning partagé, statistiques avancées, etc.

**Q : Faut-il modifier le code WinDev ?**
> Modifications minimales : configurer la connexion MySQL (si pas déjà fait) et ajouter la colonne "source" lors de la création des besoins. Le reste fonctionne de manière transparente.

---

## Annexe technique : Les tables de données

### A. Tables WinDev existantes — Base `FacturationClient`

Ces tables sont gérées par votre application WinDev/WebDev (MagicSuite). Elles contiennent vos données métier actuelles.

**Tables principales (synchronisées avec Django) :**

| Table | Contenu | Colonnes principales |
|---|---|---|
| **T_Client** | Pharmacies clientes (30+) | IDClient, NomClient, Solde, Code, Contrat, Intérieur, TelFixe, TelCel, AdresseGeo, EmailClient, NomResponsable, TelPharmacien, SousContrat, IDLocalite, ActifOP |
| **T_Utilisateur** | Techniciens et utilisateurs | IDUtilisateur, CodeUtilisateur, NomComplet, TelCel, telCel2, ActifOP, Technicien |
| **T_Intervention** | Interventions (dépannage, inventaire, maintenance...) | IDIntervention, DateIntervention, IDClient, IDTypeIntervention, IDUtilisateur, 2emeUtilisateur, NbJours, DateChoisie, DateChoisieFin, MontantTTC, Frais, ValideOP, AnnuleOP, Effectue |
| **T_Ville** | Villes (Abidjan, Soubré, Bingerville...) | IDVille, NomVille |
| **T_Localite** | Localités/Communes (Abobo, Cocody, Plateau, Port-Bouet...) | IDLocalite, NomLocalite, IDVille, Code |

**Tables de paramétrage (non synchronisées — restent dans WinDev) :**

| Table | Contenu | Données observées |
|---|---|---|
| **T_TypeIntervention** | Types d'interventions | Dépannage, Mixte, Inventaire, Maintenance, MAJ |
| **T_NatureIntervention** | Natures détaillées | Dépannage logiciel, Dépannage matériel, Dépannage réseau, Inventaire, Maintenance périodique, Mise à jour MagicSuite |
| **T_ModePaiement** | Modes de paiement | Carte bancaire, Chèque, Espèce, MoovMoney, MTN Money, Orange Money, OrangeMoney, Virement, Wave |
| **T_Prospect** | Prospects commerciaux | Nom, Responsable, Téléphone, Localité, Email, Logiciel actuel, Date logiciel, Option recherchée, Statut (Magic présenté, Contacté, RDV pris, Devenu client) |
| **T_Conge** | Congés et permissions | N° Congé, Agent, Date début, Date fin, Heure début, Heure fin, Motif |
| **T_Inventaire** | Inventaires pharmacies | Pharmacie, Dates, Nb jours intérieur, Techniciens, Montant inventaire, Montant HT, Frais financés société/technicien, Totaux |
| **T_Profil** | Profils utilisateurs | Rôles et permissions WinDev |
| **T_DetailIntervention** | Tâches d'une intervention | Tâche, Description (détail par intervention) |
| **T_FraisIntervention** | Frais d'intervention | Montant facturé, Frais intervention par technicien |

> Les tables principales sont **lues par Django** (SELECT). Les tables de paramétrage **restent exclusivement dans WinDev** (hors périmètre de sync).

### B. Tables de synchronisation — Base `FacturationClient`

Ces tables sont **partagées** entre WinDev et Django. Les deux applications y écrivent.

| Table | Rôle | Qui écrit ? |
|---|---|---|
| **T_BesoinsClient** | Besoins / demandes SAV | WinDev + Django (INSERT + UPDATE) |
| **T_DetailIntervention** | Détails des interventions | WinDev + Django (INSERT) |

**Détail des colonnes (schéma réel WinDev) :**

**T_BesoinsClient** (besoins clients) :
| Colonne | Type | Description |
|---|---|---|
| IDBesoinsClient | BIGINT (auto PK) | Identifiant unique |
| IDClient | BIGINT (FK T_Client) | Lien vers la pharmacie |
| DateBesoin | DATE | Date de la demande |
| DateAjout | TIMESTAMP | Date de création |
| HeureEnreg | TIME | Heure d'enregistrement |
| DescriptionBesoin | LONGTEXT | Description du problème |
| ValideOP | TINYINT | 0 = non validé, 1 = validé |
| Traite | TINYINT | 0 = non traité, 1 = traité |
| Annule | TINYINT | 0 = actif, 1 = annulé |
| NomTechnicien | VARCHAR(50) | Technicien assigné |
| IDUtilisateur | INTEGER | Utilisateur ayant créé |
| IDUtilisateur_Validation | INTEGER | Utilisateur ayant validé |
| IDUtilisateur_Traitement | INTEGER | Utilisateur ayant traité |
| IDUtilisateur_Annulation | INTEGER | Utilisateur ayant annulé |
| DateDernierModif | TIMESTAMP | Dernière modification |

**T_DetailIntervention** (détails d'intervention) :
| Colonne | Type | Description |
|---|---|---|
| IDDetailIntervention | BIGINT (auto PK) | Identifiant unique |
| IDIntervention | BIGINT (FK T_Intervention) | Lien vers l'intervention |
| IDNature | BIGINT (FK T_Nature) | Nature de l'intervention |
| DescriptionDetail | LONGTEXT | Description du détail |
| IDUtilisateur | BIGINT | Technicien ayant effectué |
| DateAjout | TIMESTAMP | Date de création |
| DateDernierModif | TIMESTAMP | Dernière modification |

### C. Tables Django — Base `sav_pharmacie`

Ces tables sont gérées par l'application web Django. Elles n'existent que dans la base `sav_pharmacie`.

#### Comptes et utilisateurs
| Table | Contenu | Description |
|---|---|---|
| **User** | Utilisateurs | Admins, pharmacies, techniciens (avec rôles) |

#### Pharmacies
| Table | Contenu | Description |
|---|---|---|
| **Pharmacie** | Profil pharmacie | Nom, adresse, contact, coordonnées GPS, contrat |
| **ContactPharmacie** | Contacts | Contacts additionnels d'une pharmacie |
| **EquipementPharmacie** | Équipements | Matériel/logiciel installé (pour référence SAV) |

#### Tickets SAV
| Table | Contenu | Description |
|---|---|---|
| **Ticket** | Tickets SAV | Référence, objet, catégorie, urgence, statut, dates |
| **TicketAttachment** | Pièces jointes | Fichiers attachés aux tickets |
| **TicketMessage** | Messages | Échanges pharmacie ↔ technicien sur un ticket |
| **TicketStatusHistory** | Historique statuts | Trace de chaque changement de statut |
| **TicketDelegation** | Délégations | Transfert d'un ticket entre techniciens |
| **TicketEvaluation** | Évaluations | Note et commentaire du client après résolution |

#### Interventions
| Table | Contenu | Description |
|---|---|---|
| **RapportIntervention** | Rapports | Actions, diagnostic, résultat, durée, géolocalisation, signature |
| **PhotoIntervention** | Photos | Photos prises pendant l'intervention |

#### Zones géographiques
| Table | Contenu | Description |
|---|---|---|
| **Region** | Régions | Découpage géographique principal |
| **Commune** | Communes | Communes dans une région |
| **Quartier** | Quartiers | Quartiers dans une commune |
| **Zone** | Zones de couverture | Regroupement de communes/quartiers |
| **TechnicienProfile** | Profil technicien | Zones, compétences, disponibilité, géolocalisation |

#### Notifications
| Table | Contenu | Description |
|---|---|---|
| **Notification** | Notifications | Alertes automatiques (ticket créé, assigné, résolu, message...) |

#### Synchronisation
| Table | Contenu | Description |
|---|---|---|
| **SyncCursor** | Curseurs de sync | Dernier ID/date synchronisé par entité (sync incrémentale) |
| **SyncLog** | Journaux de sync | Historique des synchronisations (succès, erreurs, compteurs) |

### D. Comment les deux applications communiquent

#### Le principe

Les deux applications (WinDev et Django) partagent le **même serveur MySQL**. Elles utilisent chacune leur propre base de données, mais peuvent lire et écrire dans des tables communes.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SERVEUR MySQL (chez vous)                       │
│                                                                     │
│  ┌──────────────────────────┐    ┌──────────────────────────┐      │
│  │   FacturationClient      │    │    sav_pharmacie          │      │
│  │   (base WinDev)          │    │    (base Django)          │      │
│  │                          │    │                           │      │
│  │   T_Client               │    │    User                   │      │
│  │   T_Utilisateur          │    │    Pharmacie              │      │
│  │   T_Intervention         │    │    Ticket                 │      │
│  │   T_Ville                │    │    RapportIntervention    │      │
│  │   T_Localite             │    │    Notification           │      │
│  │                          │    │    Region / Commune       │      │
│  │   T_BesoinsClient  ◄────┼────┼──► Ticket                 │      │
│  │   T_DetailInterv.  ◄────┼────┼──► RapportIntervention    │      │
│  │   (tables partagées)     │    │                           │      │
│  └──────────────────────────┘    └──────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         ▲                                        ▲
         │                                        │
    ┌────┴──────┐                          ┌──────┴──────┐
    │  WinDev   │                          │   Django     │
    │  Desktop  │                          │   Web/Mobile │
    └───────────┘                          └─────────────┘
```

#### Le flux de synchronisation automatique

La synchronisation est **automatique** et **bidirectionnelle**, toutes les **2 minutes** :

**Sens 1 — WinDev vers Django (vos données → l'application web) :**
```
Toutes les 2 minutes, Django lit les nouvelles données WinDev :

  T_Client       ──────►  Pharmacie         (nouveaux clients)
  T_Utilisateur  ──────►  User/Technicien   (nouveaux techniciens)
  T_Intervention ──────►  Ticket            (nouvelles interventions)
  T_BesoinsClient──────►  Ticket            (nouveaux besoins)
  T_Ville        ──────►  Region            (toutes les 15 min)
  T_Localite     ──────►  Commune           (toutes les 15 min)
```

**Sens 2 — Django vers WinDev (l'application web → vos données) :**
```
Toutes les 2 minutes, Django écrit dans les tables partagées :

  Ticket (nouveau)    ──────►  T_BesoinsClient      (INSERT avec DescriptionBesoin préfixé [SAV Web])
  Ticket (résolu)     ──────►  T_BesoinsClient      (UPDATE ValideOP, Traite)
  RapportIntervention ──────►  T_DetailIntervention  (INSERT avec DescriptionDetail préfixé [SAV Web])
  Assignation technicien ───►  T_BesoinsClient      (UPDATE NomTechnicien)
```

#### Comment ça fonctionne concrètement

1. **Un technicien ajoute un client dans WinDev**
   → En moins de 2 minutes, le client apparaît dans l'application web

2. **Une pharmacie crée un ticket SAV sur le web**
   → En moins de 2 minutes, le ticket apparaît dans WinDev (table T_BesoinsClient)

3. **Un technicien rédige un rapport sur son téléphone**
   → En moins de 2 minutes, le rapport est visible dans WinDev (table T_DetailIntervention)

4. **Un admin assigne un technicien sur le web**
   → En moins de 2 minutes, le nom du technicien est mis à jour dans WinDev

#### La sécurité de la communication

```
┌──────────────────────────────────────────────────┐
│              MESURES DE SÉCURITÉ                  │
│                                                   │
│  1. Deux utilisateurs MySQL distincts :           │
│     • sav_app  → accès complet à sav_pharmacie   │
│     • sav_sync → SELECT tout + INSERT/UPDATE      │
│                  sur 2 tables seulement            │
│                                                   │
│  2. Accès restreint par IP :                      │
│     Seul le serveur Django peut se connecter       │
│                                                   │
│  3. Pare-feu :                                    │
│     Port 3306 ouvert uniquement pour le VPS       │
│                                                   │
│  4. Séparation par préfixe :                      │
│     Django préfixe ses données avec [SAV Web]     │
│     pour les distinguer des données WinDev        │
│                                                   │
│  5. Pas de suppression :                          │
│     Django ne peut PAS supprimer de données        │
│     dans votre base WinDev                        │
└──────────────────────────────────────────────────┘
```

#### Correspondance entre les tables

| Table WinDev (FacturationClient) | ↔ | Table Django (sav_pharmacie) | Sens |
|---|---|---|---|
| T_Client | → | Pharmacie + User | WinDev → Django |
| T_Utilisateur | → | User + TechnicienProfile | WinDev → Django |
| T_Intervention | → | Ticket | WinDev → Django |
| T_Ville | → | Region | WinDev → Django |
| T_Localite | → | Commune | WinDev → Django |
| T_BesoinsClient | ← | Ticket | Django → WinDev |
| T_DetailIntervention | ← | RapportIntervention | Django → WinDev |

> Chaque enregistrement Django qui provient de WinDev conserve l'ID WinDev d'origine (ex: `windev_client_id`, `windev_intervention_id`) pour garantir la traçabilité et éviter les doublons.

---

## Prochaine étape

1. **Validation** de cette proposition
2. **Configuration** du serveur MySQL côté WinDev (1-2h avec votre équipe technique)
3. **Déploiement** de la solution sur le VPS
4. **Test** avec 2-3 pharmacies pilotes
5. **Déploiement** général

> **Nous sommes prêts à démarrer dès votre accord.**
