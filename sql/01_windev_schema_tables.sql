-- Script genere par WINDEV Suite le 11/03/2026 11:34:15
-- Tables du schema des donnees FacturationClient.wda pour MySQL
-- Partie 1 : Creation des tables (sans contraintes FK)

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- TABLES DE REFERENCE
-- ============================================================

CREATE TABLE IF NOT EXISTS `T_Sexe` (
    `IDSexe` VARCHAR(2) NOT NULL UNIQUE,
    `LibSexe` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Civilite` (
    `IDCivilite` VARCHAR(20) NOT NULL UNIQUE,
    `LibCivilite` VARCHAR(30)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Categorie` (
    `IDCategorie` VARCHAR(20) NOT NULL UNIQUE DEFAULT '0',
    `LibCategorie` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Conditionnement` (
    `IDConditionnement` VARCHAR(20) NOT NULL UNIQUE,
    `LibConditionnement` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_CodeGeo` (
    `IDCodeGeo` VARCHAR(10) NOT NULL UNIQUE,
    `LibCodeGeo` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeProduit` (
    `IDTypeProduit` VARCHAR(10) NOT NULL UNIQUE DEFAULT '0',
    `LibTypeProduit` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeClient` (
    `IDTypeClient` VARCHAR(20) NOT NULL UNIQUE,
    `LibTypeClient` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeClientFNE` (
    `IDTypeClientFNE` VARCHAR(10) NOT NULL UNIQUE,
    `LibTypeClientFNE` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeFournisseur` (
    `IDTypeFournisseur` VARCHAR(2) NOT NULL UNIQUE DEFAULT 'D',
    `LibTypeFournisseur` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeIntervention` (
    `IDTypeIntervention` VARCHAR(20) NOT NULL UNIQUE,
    `LibTypeIntervention` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeInventaire` (
    `IDTypeInventaire` VARCHAR(20) NOT NULL UNIQUE,
    `LibTypeInventaire` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeMvt` (
    `IDTypeMvt` VARCHAR(10) NOT NULL UNIQUE DEFAULT '0',
    `LibtypeMvt` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeConnexion` (
    `CodeTypeConnexion` VARCHAR(20) NOT NULL UNIQUE,
    `LibelleTypeConnexion` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeContrat` (
    `IDTypeContrat` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `LibTypeContrat` VARCHAR(50) UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TypeLicence` (
    `IDTypeLicence` VARCHAR(1) NOT NULL UNIQUE,
    `LibTypeLicence` VARCHAR(50) NOT NULL UNIQUE,
    `DateDernierModif` DATE,
    `DateAjout` DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_TVA` (
    `TauxTVA` SMALLINT NOT NULL UNIQUE DEFAULT 0,
    `FNE_TypeTaxe` VARCHAR(10),
    `FNE_DescriptionTypeTxe` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_AutresTaxe` (
    `IDAutreTaxe` VARCHAR(20) UNIQUE,
    `LibAutreTaxe` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_ModePaiement` (
    `IDModePaiement` VARCHAR(10) NOT NULL UNIQUE DEFAULT '0',
    `LibModePaiement` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_EtatCommande` (
    `IDEtatCde` VARCHAR(2) NOT NULL UNIQUE,
    `LibEtatCde` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_MotifMvt` (
    `IDMotifMvt` VARCHAR(10) NOT NULL UNIQUE,
    `LibMotifMvt` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Groupe` (
    `IDGroupe` VARCHAR(5) NOT NULL UNIQUE,
    `LibGroupe` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Famille` (
    `IDFamille` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `CodeFamille` VARCHAR(15),
    `LibFamille` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Formes` (
    `IDForme` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `LibForme` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Libel_Ventil_CA` (
    `CODE_VENTIL_CA` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `LIB_VENTIL_CA` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Nature` (
    `IDNature` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `LibNature` VARCHAR(100),
    `DateAjout` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_PeriodiciteContrat` (
    `IDPeriodiciteContrat` VARCHAR(20) NOT NULL UNIQUE,
    `LibPeriodiciteContrat` VARCHAR(50) UNIQUE,
    `NbJoursPeriode` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_PARAMETRE` (
    `NOMPARAMETRE` VARCHAR(50),
    `VALEURPARAMETRE` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_NumeroFacture` (
    `IDNumeroFacture` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `PrefixeNumFacture` VARCHAR(10),
    `IncrementNumFacture` INTEGER DEFAULT 0,
    `AnneeFacture` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES PRINCIPALES
-- ============================================================

CREATE TABLE IF NOT EXISTS `T_Ville` (
    `IDVille` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomVille` VARCHAR(50) UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Localite` (
    `IDLocalite` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomLocalite` VARCHAR(50),
    `IDVille` BIGINT DEFAULT 0,
    `DateAjout` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    `DateDernierModif` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_ProfilUtilisateur` (
    `IDProfil` VARCHAR(20) NOT NULL UNIQUE,
    `NomProfil` VARCHAR(50) UNIQUE,
    `DescriptionProfil` VARCHAR(200),
    `ActifOP` TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_CabinetComptable` (
    `IDCabinetComptable` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomCabinet` VARCHAR(50),
    `nomresponsable` VARCHAR(50),
    `Tel` VARCHAR(20),
    `Tel2` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Utilisateur` (
    `IDUtilisateur` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `CodeUtilisateur` VARCHAR(20) UNIQUE,
    `ActifOP` TINYINT DEFAULT 0,
    `AccesApplication` TINYINT DEFAULT 0,
    `OP_Cde_Saisie` TINYINT DEFAULT 0,
    `OP_Cde_Modif` TINYINT DEFAULT 0,
    `OP_Cde_Suppr` TINYINT DEFAULT 0,
    `DateAjout` DATE,
    `OP_Mvt_Suppr` TINYINT DEFAULT 0,
    `OP_Mvt_Perime` TINYINT DEFAULT 0,
    `OP_Mvt_Entree` TINYINT DEFAULT 0,
    `OP_Mvt_Decondition` TINYINT DEFAULT 0,
    `OP_Mvt_RetourFour` TINYINT DEFAULT 0,
    `OP_User_Acces` TINYINT DEFAULT 0,
    `OP_User_Modif` TINYINT DEFAULT 0,
    `OP_Param_Std_Acces` TINYINT DEFAULT 0,
    `OP_Param_Std_Modif` TINYINT DEFAULT 0,
    `OP_Param_Std_Suppr` TINYINT DEFAULT 0,
    `MotDePasse_OP` VARCHAR(40),
    `NomComplet` VARCHAR(50),
    `OP_Cde_ReceptionDefinitive` TINYINT DEFAULT 0,
    `OP_Prod_Saisie` TINYINT DEFAULT 0,
    `OP_Prod_Modif` TINYINT DEFAULT 0,
    `OP_Prod_Suppr` TINYINT DEFAULT 0,
    `InitialUtilisateur` VARCHAR(10),
    `DateValidite_Debut` DATE,
    `DateValidite_Fin` DATE,
    `OP_Mvt_Sortie` TINYINT DEFAULT 0,
    `OP_Inv_Saisie` TINYINT DEFAULT 0,
    `OP_Inv_Validation` TINYINT DEFAULT 0,
    `OP_Inv_Suppr` TINYINT DEFAULT 0,
    `OP_Stat_Elementaire` TINYINT DEFAULT 0,
    `OP_Stat_Avancee` TINYINT DEFAULT 0,
    `DateDernierModif` DATE,
    `IDProfil` VARCHAR(20),
    `OP_Vente_Comptant` TINYINT DEFAULT 0,
    `OP_Vente_ACredit` TINYINT DEFAULT 0,
    `OP_Vente_Modif` TINYINT DEFAULT 0,
    `OP_Vente_Suppr` TINYINT DEFAULT 0,
    `OP_Vente_Acces` TINYINT DEFAULT 0,
    `OP_Mvt_Acces` TINYINT DEFAULT 0,
    `OP_Cde_Acces` TINYINT DEFAULT 0,
    `OP_Inv_Acces` TINYINT DEFAULT 0,
    `OP_Cde_ReceptionPartiel` TINYINT DEFAULT 0,
    `OP_Vente_Remise` TINYINT DEFAULT 0,
    `OP_Vente_ModifPrix` TINYINT DEFAULT 0,
    `OP_CLient_Modif` TINYINT DEFAULT 0,
    `OP_Depense_Saisie` TINYINT DEFAULT 0,
    `OP_Vente_RemiseEncais` TINYINT DEFAULT 0,
    `OP_Vente_Billettage` TINYINT DEFAULT 0,
    `OP_Vente_Cheque` TINYINT DEFAULT 0,
    `OP_Param_Avance_Acces` TINYINT DEFAULT 0,
    `OP_Param_Avance_Modif` TINYINT DEFAULT 0,
    `OP_Param_Avance_Suppr` TINYINT DEFAULT 0,
    `OP_Vente_SupprVenteAT` TINYINT DEFAULT 0,
    `OP_Vente_MiseEnAttente` TINYINT DEFAULT 0,
    `OP_Menu_AccesFacturation` TINYINT DEFAULT 0,
    `OP_Menu_AccesStock` TINYINT DEFAULT 0,
    `OP_Encaissement` TINYINT DEFAULT 0,
    `OP_Journal_Acces` TINYINT DEFAULT 0,
    `OP_Journal_Suppr` TINYINT DEFAULT 0,
    `OP_Journal_Creer` TINYINT DEFAULT 0,
    `OP_Proforma_Acces` TINYINT DEFAULT 0,
    `OP_Proforma_Saisie` TINYINT DEFAULT 0,
    `OP_Proforma_Modif` TINYINT DEFAULT 0,
    `OP_Proforma_Suppr` TINYINT DEFAULT 0,
    `OP_Releve_Creer` TINYINT DEFAULT 0,
    `OP_Releve_Imprimer` TINYINT DEFAULT 0,
    `OP_Releve_Supprimer` TINYINT DEFAULT 0,
    `OP_Releve_Regler` TINYINT DEFAULT 0,
    `OP_Stat_Acces_Menu` TINYINT DEFAULT 0,
    `OP_Impression` TINYINT DEFAULT 0,
    `OP_Menu_AccesContrat` TINYINT DEFAULT 0,
    `OP_Contrat_Saisie` TINYINT DEFAULT 0,
    `OP_Contrat_Modif` TINYINT DEFAULT 0,
    `OP_Contrat_Suppr` TINYINT DEFAULT 0,
    `OP_Client_Acces` TINYINT DEFAULT 0,
    `Cree_Par` VARCHAR(20),
    `Disponible` TINYINT DEFAULT 0,
    `Modifie_Par` VARCHAR(20),
    `OP_Comptabilite_Acces` TINYINT DEFAULT 0,
    `OP_Comptabilite_Modif` TINYINT DEFAULT 0,
    `OP_Comptabilite_Saisie` TINYINT DEFAULT 0,
    `OP_Comptabilite_Suppr` TINYINT DEFAULT 0,
    `OP_Intervention_Approuver` TINYINT DEFAULT 0,
    `OP_Intervention_Modif` TINYINT DEFAULT 0,
    `OP_Intervention_Saisie` TINYINT DEFAULT 0,
    `OP_Intervention_Suppr` TINYINT DEFAULT 0,
    `OP_Inventaire_CalculFrais` TINYINT DEFAULT 0,
    `OP_Reglement_Saisie` TINYINT DEFAULT 0,
    `OP_Reglement_Modif` TINYINT DEFAULT 0,
    `OP_Reglement_Suppr` TINYINT DEFAULT 0,
    `Technicien` TINYINT DEFAULT 0,
    `TelCel` VARCHAR(30),
    `telCel2` VARCHAR(20),
    `OP_Client_Suppr` TINYINT DEFAULT 0,
    `OP_Menu_AccesIntervention` TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Client` (
    `IDClient` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomClient` VARCHAR(100),
    `TelFixe` VARCHAR(30),
    `TelCel` VARCHAR(30),
    `Code_2ST` VARCHAR(10),
    `BoitePostale` VARCHAR(50),
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `Solde` INTEGER DEFAULT 0,
    `CreditMaxi` INTEGER DEFAULT 0,
    `TauxRemise` SMALLINT DEFAULT 0,
    `ACredit` TINYINT DEFAULT 0,
    `EmailClient` VARCHAR(50),
    `IDSexe` VARCHAR(2),
    `IDCivilite` VARCHAR(20),
    `AdresseGeo` VARCHAR(50),
    `DatePassage` DATE,
    `AcompteFacture` INTEGER DEFAULT 0,
    `Caution` INTEGER DEFAULT 0,
    `CreePar` VARCHAR(20),
    `ModifiePar` VARCHAR(20),
    `Datemodif` DATE,
    `AppliquerPrixPublic` TINYINT DEFAULT 0,
    `IDTypeClient` VARCHAR(20),
    `HeureModif` TIME,
    `Num_Compte` INTEGER DEFAULT 0,
    `Solde_Compte` INTEGER DEFAULT 0,
    `Nom_Ordinateur` NVARCHAR(20),
    `SoldeDepotVente` INTEGER DEFAULT 0,
    `NomResponsable` VARCHAR(50),
    `IDLocalite` BIGINT DEFAULT 0,
    `InterieurPays` TINYINT DEFAULT 0,
    `SousContrat` TINYINT DEFAULT 0,
    `TelPharmacien` VARCHAR(15),
    `IDUtilisateur` BIGINT DEFAULT 0,
    `ClientHorsM` TINYINT DEFAULT 0,
    `NCC_Client` VARCHAR(30),
    `Commune_Client` VARCHAR(30),
    `Civilite` VARCHAR(10),
    `DateMaintenance` DATE,
    `IDCabinetComptable` BIGINT,
    `ActifOP` TINYINT DEFAULT 0,
    `telCel2` VARCHAR(20),
    `MontantInventaire` INTEGER DEFAULT 0,
    `MontantContrat` INTEGER DEFAULT 0,
    `RCC_Client` VARCHAR(30),
    `IDTypeClientFNE` VARCHAR(10)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Client_Prospect` (
    `IDClient` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomClient` VARCHAR(100),
    `TelFixe` VARCHAR(30),
    `TelCel` VARCHAR(30),
    `EmailClient` VARCHAR(50),
    `Code_2ST` VARCHAR(10),
    `IDLocalite` BIGINT DEFAULT 0,
    `IDUtilisateur` INTEGER DEFAULT 0,
    `ActifOP` TINYINT DEFAULT 0,
    `DateAjout` TIMESTAMP,
    `DateDernierModif` TIMESTAMP,
    `NomResponsable` VARCHAR(50),
    `AdresseGeo` VARCHAR(100),
    `DateLogiciel` DATE,
    `NomLogicielActuel` VARCHAR(50),
    `OptionRecherchee` VARCHAR(100),
    `RappelerPharmacien` TINYINT DEFAULT 0,
    `PresentationMagicSuite` TINYINT DEFAULT 0,
    `PresentationAutreLogiciel` TINYINT DEFAULT 0,
    `DevenuClient` TINYINT DEFAULT 0,
    `DejaContacte` TINYINT DEFAULT 0,
    `InterieurPays` TINYINT DEFAULT 0,
    `RDVPris` TINYINT DEFAULT 0,
    `RDVDate` DATE,
    `RDVEffectue` TINYINT DEFAULT 0,
    `TelResponsable` VARCHAR(15)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_fournisseur` (
    `IDFournisseur` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomFournisseur` VARCHAR(50),
    `TelFournisseur` VARCHAR(30),
    `TelFournisseur2` VARCHAR(30),
    `FaxFournisseur` VARCHAR(15),
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `EmailFournisseur` VARCHAR(50),
    `CreePar` VARCHAR(20),
    `ModifiePar` VARCHAR(20),
    `Datemodif` DATE,
    `AdresseGeo` VARCHAR(50),
    `SoldeFournisseur` INTEGER DEFAULT 0,
    `IDTypeFournisseur` VARCHAR(2) DEFAULT 'D',
    `NomContact` VARCHAR(50),
    `TelContact` VARCHAR(20),
    `FournisseurActif` TINYINT DEFAULT 0,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDUtilisateur_Modif` BIGINT DEFAULT 0,
    `HeureModif` TIME,
    `NCC_Four` VARCHAR(30),
    `RCC_Four` VARCHAR(30)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_produit` (
    `IDProduit` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `CodeCIP` VARCHAR(20) UNIQUE DEFAULT '0',
    `PUAchatTTC` INTEGER DEFAULT 0,
    `PUVenteTTC` INTEGER DEFAULT 0,
    `FraisGeneraux` TINYINT DEFAULT 0,
    `Designation` VARCHAR(50) UNIQUE,
    `DepotVente` TINYINT DEFAULT 0,
    `StockGlobal` INTEGER DEFAULT 0,
    `QteMaxi` INTEGER DEFAULT 0,
    `QteMini` INTEGER DEFAULT 0,
    `StockAlert` INTEGER DEFAULT 0,
    `PUVenteHT` INTEGER DEFAULT 0,
    `PUAchatHT` INTEGER DEFAULT 0,
    `TauxTVA` SMALLINT DEFAULT 0,
    `SurInventaire` TINYINT DEFAULT 0,
    `ProduitActif` TINYINT DEFAULT 0,
    `IDTypeProduit` VARCHAR(10) DEFAULT '0',
    `CreePar` VARCHAR(20),
    `ModifiePar` VARCHAR(20),
    `RemiseMaxi` INTEGER DEFAULT 0,
    `Qte_DetailParBoite` INTEGER DEFAULT 0,
    `Pk_Detail` INTEGER DEFAULT 0,
    `Remisable` TINYINT DEFAULT 0,
    `ModifieLe` DATE,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `DateDernierAchat` DATE,
    `DateDerniereVente` DATE,
    `IDGroupe` VARCHAR(5),
    `IDFamille` BIGINT DEFAULT 0,
    `IDCategorie` VARCHAR(20),
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDUtilisateur_Modif` BIGINT DEFAULT 0,
    `IDFournisseur` BIGINT DEFAULT 0,
    `DatePremierAchat` DATE,
    `DatePremiereVente` DATE,
    `Mini_Maxi_Bloquer` TINYINT DEFAULT 0,
    `ReferenceProd` VARCHAR(20) UNIQUE,
    `QtUnitAchat` INTEGER DEFAULT 0,
    `IDCodeGeo` VARCHAR(10),
    `PasDeconditionAuto` TINYINT DEFAULT 0,
    `VenteAutorise` TINYINT DEFAULT 0,
    `AchatAutorise` TINYINT DEFAULT 0,
    `IDConditionnement` VARCHAR(20),
    `PUPublicTTC` INTEGER DEFAULT 0,
    `PUPublicHT` INTEGER DEFAULT 0,
    `Coef_Px` INTEGER DEFAULT 0,
    `DateModif` DATE,
    `HeureModif` TIME,
    `Qte_UG` INTEGER DEFAULT 0,
    `Code_Ventil_CA` BIGINT DEFAULT 0,
    `IDForme` BIGINT,
    `Moyenne_Mois` INTEGER DEFAULT 0,
    `GererStock` TINYINT DEFAULT 0,
    `HeureAjout` TIME,
    `HeureDerniereModif` TIME,
    `ServiceFacture` TINYINT DEFAULT 0,
    `Perissable` TINYINT DEFAULT 0,
    `CodeCIP2` VARCHAR(20),
    `CodeCIP3` VARCHAR(20),
    `CodeCIP4` VARCHAR(20),
    `CodeCIP5` VARCHAR(20),
    `CodeCIP6` VARCHAR(20),
    `CodeCIP7` VARCHAR(20),
    `StockDepotVente` INTEGER DEFAULT 0,
    `PUPublicTTCMini` INTEGER DEFAULT 0,
    `PUVenteTTCMini` INTEGER DEFAULT 0,
    `Contrat` TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_CodeCIP` (
    `IDCodecip` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `CodeCipProduit` INTEGER DEFAULT 0,
    `IDProduit` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_LotProduit` (
    `IDLotProduit` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDProduit` BIGINT,
    `NumLot` VARCHAR(20),
    `DatePeremption` DATE,
    `QteLot` INTEGER DEFAULT 0,
    `IDCodeGeo` VARCHAR(10),
    `DateAjout` DATE,
    `DateDernierModif` DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_KitProduit` (
    `IDKitProduit` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDProduitKit` BIGINT,
    `IDProduitDetailKit` BIGINT,
    `QteDetail` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES INTERVENTION / SAV (SYNCHRONISATION)
-- ============================================================

CREATE TABLE IF NOT EXISTS `T_Intervention` (
    `IDIntervention` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateIntervention` DATE,
    `IDClient` BIGINT,
    `IDTypeIntervention` VARCHAR(20),
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDIntervention2emeUtilisateur` BIGINT DEFAULT 0,
    `ValideOP` TINYINT DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `EffectueOP` TINYINT DEFAULT 0,
    `NbJours` INTEGER DEFAULT 0,
    `DatePlanifie1` DATE,
    `DatePlanifie1_Fin` DATE,
    `DatePlanifie2` DATE,
    `DateChoisie` DATE,
    `DateChoisieFin` DATE,
    `MontantTTC` INTEGER DEFAULT 0,
    `Frais_Technicien` INTEGER DEFAULT 0,
    `IDUtilisateur_Saisie` BIGINT DEFAULT 0,
    `IDUtilisateur_Modif` BIGINT DEFAULT 0,
    `IDUtilisateur_Validation` INTEGER DEFAULT 0,
    `IDUtilisateur_annul` INTEGER DEFAULT 0,
    `HeureEnreg` TIME,
    `NomTechnicien` VARCHAR(50),
    `DateAjout` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    `DateDernierModif` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Nature_TypeIntervention` (
    `IDNature_TypeIntervention` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDTypeIntervention` VARCHAR(20),
    `IDNature` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_DetailIntervention` (
    `IDDetailIntervention` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDIntervention` BIGINT,
    `IDNature` BIGINT,
    `DescriptionDetail` LONGTEXT,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `DateAjout` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    `DateDernierModif` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_BesoinsClient` (
    `IDBesoinsClient` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateBesoin` DATE,
    `DateAjout` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    `HeureEnreg` TIME,
    `DescriptionBesoin` LONGTEXT,
    `ValideOP` TINYINT DEFAULT 0,
    `Traite` TINYINT DEFAULT 0,
    `Annule` TINYINT DEFAULT 0,
    `NomTechnicien` VARCHAR(50),
    `IDClient` BIGINT,
    `IDUtilisateur` INTEGER DEFAULT 0,
    `IDUtilisateur_Validation` INTEGER DEFAULT 0,
    `IDUtilisateur_Traitement` INTEGER DEFAULT 0,
    `IDUtilisateur_Annulation` INTEGER DEFAULT 0,
    `DateDernierModif` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_InventaireClient` (
    `IDInventaireClient` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDClient` BIGINT,
    `IDIntervention` BIGINT,
    `DateInventaire` DATE,
    `MontantInventaire` INTEGER DEFAULT 0,
    `DateAjout` TIMESTAMP,
    `DateDernierModif` TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_ConnexionServeur` (
    `IDConnexionServeur` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `ComptePharmacien` VARCHAR(50),
    `PWDPharmacien` VARCHAR(30),
    `PWDAdmin` VARCHAR(30),
    `CompteAdmin` VARCHAR(50),
    `AdresseConnexion` VARCHAR(50),
    `IDClient` BIGINT,
    `PWDConnexion` VARCHAR(30),
    `NomClient` VARCHAR(100),
    `CodeTypeConnexion` VARCHAR(20),
    `CompteGroupe` VARCHAR(50),
    `PWDGroupe` VARCHAR(30)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES FACTURATION / VENTE
-- ============================================================

CREATE TABLE IF NOT EXISTS `T_ReleveClient` (
    `IDReleveClient` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `Date_Edition` DATE,
    `MontantTTC` INTEGER DEFAULT 0,
    `SoldeReleve` INTEGER DEFAULT 0,
    `MontantRegle` INTEGER DEFAULT 0,
    `DateReglement` DATE,
    `DateReelEdition` DATE,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `RefReleve` VARCHAR(20),
    `DateDebut` DATE,
    `DateFin` DATE,
    `AnnuleOP` TINYINT DEFAULT 0,
    `MontantHT` INTEGER DEFAULT 0,
    `MontantTVA` INTEGER DEFAULT 0,
    `NomClient` VARCHAR(100),
    `IDClient` BIGINT,
    `IDUtilisateur` BIGINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Contrat` (
    `IDContrat` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DescriptionContrat` VARCHAR(100),
    `DateAjout` DATE,
    `MontantHT` INTEGER DEFAULT 0,
    `MontantTVA` INTEGER DEFAULT 0,
    `MontantTTC` INTEGER DEFAULT 0,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDUtilisateur_Modif` BIGINT DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `DateDebut` DATE,
    `DateFin` DATE,
    `IDClient` BIGINT,
    `NomClient` VARCHAR(100),
    `Datemodif` DATE,
    `CreePar` VARCHAR(20),
    `ModifiePar` VARCHAR(20),
    `AnnulePar` VARCHAR(20),
    `Date_Annulation` DATE,
    `NbLignes` INTEGER DEFAULT 0,
    `SoldeContrat` INTEGER DEFAULT 0,
    `IDTypeContrat` BIGINT,
    `IDPeriodiciteContrat` VARCHAR(20),
    `DateDerniereFacture` DATE,
    `TermineOP` TINYINT DEFAULT 0,
    `HeureDebut` DATE,
    `HeureFin` TIME,
    `Code_2ST` VARCHAR(10),
    `MonantInventaire` INTEGER DEFAULT 0,
    `FichierContrat` LONGBLOB
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Factures` (
    `IDFacture` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateFacture` DATE,
    `IDClient` BIGINT DEFAULT 0,
    `NomClient` VARCHAR(100),
    `MtVenteTTC` INTEGER DEFAULT 0,
    `MtVenteHT` INTEGER DEFAULT 0,
    `MtVenteTVA` INTEGER DEFAULT 0,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `MtRemise` INTEGER DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `IDModePaiement` VARCHAR(10),
    `MtRegle` INTEGER DEFAULT 0,
    `MtMonnaie` INTEGER DEFAULT 0,
    `HeureFacture` TIME,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `IDReleveClient` BIGINT,
    `NbLignes` INTEGER DEFAULT 0,
    `CreePar` VARCHAR(20),
    `ModifiePar` VARCHAR(20),
    `AnnulePar` VARCHAR(20),
    `NumBande` INTEGER DEFAULT 0,
    `MtAchatHT` INTEGER DEFAULT 0,
    `MtAchatTTC` INTEGER DEFAULT 0,
    `MargeFacture` INTEGER DEFAULT 0,
    `Nom_Ordinateur` NVARCHAR(20),
    `NumFacture` VARCHAR(20),
    `IDContrat` BIGINT,
    `IDSessionCaisse` BIGINT,
    `DateAnnul` DATE,
    `Vendeur` VARCHAR(20),
    `ServiceFacture` TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Factures_AT` (
    `IDFacture` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateFacture` DATE,
    `IDClient` BIGINT DEFAULT 0,
    `NomClient` VARCHAR(100),
    `MtVenteTTC` INTEGER DEFAULT 0,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `NbLignes` INTEGER DEFAULT 0,
    `Nom_Ordinateur` NVARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_lignes` (
    `IDLigne` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDFacture` BIGINT DEFAULT 0,
    `codeCIP` VARCHAR(20) DEFAULT '0',
    `IDClient` BIGINT DEFAULT 0,
    `DateFacture` DATE,
    `TYPE_LIGNE` NVARCHAR(10),
    `PX_BASE_TTC` DOUBLE DEFAULT 0,
    `PUVenteTTC` INTEGER DEFAULT 0,
    `REMISE_LIGNE` INTEGER DEFAULT 0,
    `QT_STOCK_AVANT` INTEGER DEFAULT 0,
    `IDProduit` BIGINT DEFAULT 0,
    `QT_SORTI` INTEGER DEFAULT 0,
    `Qte_Vendu` INTEGER DEFAULT 0,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `CODE_ACTE` TINYINT,
    `CODE_FAMILLE_STD` NVARCHAR(15),
    `TauxTVA` SMALLINT DEFAULT 0,
    `PUVenteHT` INTEGER DEFAULT 0,
    `CODE_VENTIL_CA` BIGINT DEFAULT 0,
    `PUAchatHT` INTEGER DEFAULT 0,
    `MANQUANTS` NVARCHAR(10) DEFAULT '0',
    `POURCENT_TP_P` INTEGER DEFAULT 0,
    `POURCENT_TP_C` INTEGER DEFAULT 0,
    `PK_REGIME_P` INTEGER DEFAULT 0,
    `PK_REGIME_C` INTEGER DEFAULT 0,
    `CODE_LISTE` VARCHAR(2) DEFAULT '0',
    `NUM_ORDONNAN` INTEGER DEFAULT 0,
    `IDGroupe` VARCHAR(5),
    `ETAT_LIGNE` NVARCHAR(1),
    `IDFamille` BIGINT,
    `PK_AVANCE` BIGINT DEFAULT 0,
    `QT_DANS_UNIT_ACHAT` INTEGER DEFAULT 0,
    `PX_ACHAT_REEL_HT` INTEGER DEFAULT 0,
    `CODE_ORIGINE` NVARCHAR(5),
    `PRODUIT_HCAISSE` TINYINT DEFAULT 0,
    `PK_PRODUIT_SORTI` INTEGER DEFAULT 0,
    `NUM_CAISSE` INTEGER DEFAULT 0,
    `DESIGNATION` VARCHAR(50),
    `Total_LIGNES` INTEGER DEFAULT 0,
    `IDCodeGeo` VARCHAR(10),
    `HEUREAJOUT` TIME,
    `Poste_Nom` VARCHAR(50),
    `Poste_AdresseIP` VARCHAR(50),
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `NumLigne` INTEGER DEFAULT 0,
    `Nom_Ordinateur` NVARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_lignes_AT` (
    `IDLigne` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDFacture` BIGINT DEFAULT 0,
    `IDProduit` BIGINT DEFAULT 0,
    `Designation` VARCHAR(50),
    `PUVenteTTC` INTEGER DEFAULT 0,
    `Qte_Vendu` INTEGER DEFAULT 0,
    `Total_LIGNES` INTEGER DEFAULT 0,
    `DateAjout` DATE,
    `Nom_Ordinateur` NVARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Lignes_Annul` (
    `IDLigne` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDFacture` BIGINT DEFAULT 0,
    `IDProduit` BIGINT DEFAULT 0,
    `Designation` VARCHAR(50),
    `PUVenteTTC` INTEGER DEFAULT 0,
    `Qte_Vendu` INTEGER DEFAULT 0,
    `Total_LIGNES` INTEGER DEFAULT 0,
    `DateAjout` DATE,
    `AnnulePar` VARCHAR(20),
    `DateAnnul` DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `Log_LIGNESVTE1` (
    `NUM_LIGNE` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDFacture` BIGINT DEFAULT 0,
    `codeCIP` VARCHAR(20) DEFAULT '0',
    `IDClient` BIGINT DEFAULT 0,
    `DateFacture` DATE,
    `TYPE_LIGNE` NVARCHAR(10),
    `PX_BASE_TTC` DOUBLE DEFAULT 0,
    `PUVenteTTC` INTEGER DEFAULT 0,
    `REMISE_LIGNE` INTEGER DEFAULT 0,
    `QT_STOCK_AVANT` INTEGER DEFAULT 0,
    `IDProduit` BIGINT DEFAULT 0,
    `QT_SORTI` INTEGER DEFAULT 0,
    `Qte_Vendu` INTEGER DEFAULT 0,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `CODE_ACTE` TINYINT,
    `CODE_FAMILLE_STD` NVARCHAR(15),
    `TauxTVA` SMALLINT DEFAULT 0,
    `PUVenteHT` INTEGER DEFAULT 0,
    `CODE_VENTIL_CA` BIGINT DEFAULT 0,
    `PUAchatHT` INTEGER DEFAULT 0,
    `MANQUANTS` NVARCHAR(10) DEFAULT '0',
    `POURCENT_TP_P` INTEGER DEFAULT 0,
    `POURCENT_TP_C` INTEGER DEFAULT 0,
    `PK_REGIME_P` INTEGER DEFAULT 0,
    `PK_REGIME_C` INTEGER DEFAULT 0,
    `CODE_LISTE` VARCHAR(2) DEFAULT '0',
    `NUM_ORDONNAN` INTEGER DEFAULT 0,
    `IDGroupe` VARCHAR(5),
    `ETAT_LIGNE` NVARCHAR(1),
    `IDFamille` BIGINT,
    `PK_AVANCE` BIGINT DEFAULT 0,
    `QT_DANS_UNIT_ACHAT` INTEGER DEFAULT 0,
    `PX_ACHAT_REEL_HT` INTEGER DEFAULT 0,
    `CODE_ORIGINE` NVARCHAR(5),
    `PRODUIT_HCAISSE` TINYINT DEFAULT 0,
    `PK_PRODUIT_SORTI` INTEGER DEFAULT 0,
    `NUM_CAISSE` INTEGER DEFAULT 0,
    `DESIGNATION` VARCHAR(50),
    `Total_LIGNES` INTEGER DEFAULT 0,
    `IDCodeGeo` VARCHAR(10),
    `HEUREAJOUT` TIME,
    `Poste_Nom` VARCHAR(50),
    `Poste_AdresseIP` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES CAISSE / PAIEMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS `T_SessionCaisse` (
    `IDSessionCaisse` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `DateOuverture` DATE,
    `DateFermeture` TIMESTAMP,
    `FondCaisse` NUMERIC(24,6) DEFAULT 0,
    `EtatSession` TINYINT DEFAULT 0,
    `IDT_Cloture_Journal` BIGINT DEFAULT 0,
    `HEUREouverture` TIME,
    `heureFermeture` TIME,
    `numposte` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Caisse` (
    `IDCaisse` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDFacture` BIGINT DEFAULT 0,
    `DateOperation` DATE,
    `IDClient` BIGINT DEFAULT 0,
    `Nomclient` VARCHAR(100),
    `debit` INTEGER DEFAULT 0,
    `credit` INTEGER DEFAULT 0,
    `Solde` INTEGER DEFAULT 0,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `HeureOperation` TIME,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `TypeOperation` VARCHAR(2),
    `IDModePaiement` VARCHAR(10),
    `NumEncais` BIGINT DEFAULT 0,
    `MtRemise` INTEGER DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `AnnulePar` VARCHAR(20),
    `DateAnnul` DATE,
    `CreePar` VARCHAR(20),
    `Recouvrement` TINYINT DEFAULT 0,
    `IDReleveClient` BIGINT DEFAULT 0,
    `Monnaie` INTEGER DEFAULT 0,
    `MtRemiseEncais` INTEGER DEFAULT 0,
    `LibModePaiement` VARCHAR(20),
    `Remise_Enc` INTEGER DEFAULT 0,
    `Num_Bande` INTEGER DEFAULT 0,
    `Base_TVA1` DOUBLE DEFAULT 0,
    `Base_TVA2` DOUBLE DEFAULT 0,
    `Base_TVA3` DOUBLE DEFAULT 0,
    `Montant_TVA1` DOUBLE DEFAULT 0,
    `Montant_TVA2` DOUBLE DEFAULT 0,
    `Montant_TVA3` DOUBLE DEFAULT 0,
    `MtRecu` INTEGER DEFAULT 0,
    `IDSessionCaisse` BIGINT,
    `Datemodif` DATE,
    `Mont_Horscaisse` BIGINT DEFAULT 0,
    `Marge` BIGINT DEFAULT 0,
    `PK_PAYEUR` DOUBLE DEFAULT 0,
    `ETAT_LIGNE_CAISSE` NVARCHAR(1),
    `OP_AUTORISATION` INTEGER DEFAULT 0,
    `Vendeur` VARCHAR(20),
    `PETITEMONNAIE` INTEGER DEFAULT 0,
    `ServiceFacture` TINYINT DEFAULT 0,
    `NumFacture` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_CHEQUES` (
    `IDCaisse` BIGINT DEFAULT 0,
    `IDCheque` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomClient` VARCHAR(100),
    `MONTANT_CHEQUE` DOUBLE DEFAULT 0,
    `BANQUE_CLIENT` NVARCHAR(255),
    `DATE_ENCAISSEMENT` TIMESTAMP DEFAULT '1970-01-01 00:00:01',
    `HORSPLACE` NVARCHAR(255),
    `BANQUE2` NVARCHAR(255),
    `DATE_DEPOT` TIMESTAMP DEFAULT '1970-01-01 00:00:01',
    `NUM_BORD` DOUBLE DEFAULT 0,
    `CHEQUERECU` TINYINT DEFAULT 1,
    `IDClient` BIGINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Caution_Client` (
    `IDCaisse` BIGINT DEFAULT 0,
    `IDCautionClient` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDClient` BIGINT DEFAULT 0,
    `Date_caution` DATE,
    `Montant_caution` INTEGER DEFAULT 0,
    `MODE_RG` NVARCHAR(50),
    `NumCheque` VARCHAR(50),
    `banque` VARCHAR(50),
    `PK_ASSURANCE` BIGINT DEFAULT 0,
    `IDSessionCaisse` BIGINT DEFAULT 0,
    `HeureDesaisie` TIME,
    `IDModePaiement` VARCHAR(10),
    `DateAjout` DATE,
    `DateDernierModif` DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Billetage` (
    `IDBilletage` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `Piece5` INTEGER DEFAULT 0,
    `Piece10` INTEGER DEFAULT 0,
    `Piece25` INTEGER DEFAULT 0,
    `Piece50` INTEGER DEFAULT 0,
    `Piece100` INTEGER DEFAULT 0,
    `DateAjout` DATE,
    `Piece200` INTEGER DEFAULT 0,
    `Piece250` INTEGER DEFAULT 0,
    `TotalPiece` INTEGER DEFAULT 0,
    `Billet500` INTEGER DEFAULT 0,
    `Billet1000` INTEGER DEFAULT 0,
    `Billet2000` INTEGER DEFAULT 0,
    `Billet5000` INTEGER DEFAULT 0,
    `Billet10000` INTEGER DEFAULT 0,
    `TotalBillet` INTEGER DEFAULT 0,
    `OrangeMoney` INTEGER DEFAULT 0,
    `MTNMoney` INTEGER DEFAULT 0,
    `MoovMoney` INTEGER DEFAULT 0,
    `Carte` INTEGER DEFAULT 0,
    `TotalEspece` INTEGER DEFAULT 0,
    `TotalAutreReglement` INTEGER DEFAULT 0,
    `DateVersement` INTEGER DEFAULT 0,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `EffectuePar` VARCHAR(20),
    `Piece500` INTEGER DEFAULT 0,
    `TotalCheque` INTEGER DEFAULT 0,
    `DateDernierModif` DATE,
    `DateModif` DATE,
    `ModifiePar` VARCHAR(20),
    `FondDeCaisse` INTEGER DEFAULT 0,
    `ValeurStock` INTEGER DEFAULT 0,
    `NUM_BANDE` INTEGER DEFAULT 0,
    `DateAnnul` DATE,
    `TotalVersement` INTEGER DEFAULT 0,
    `NomCaissiere` VARCHAR(20),
    `HeureModif` TIME,
    `heureVersement` TIME,
    `HeureAnnul` TIME,
    `AnnulePar` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_reglement` (
    `IDReglement` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomClient` VARCHAR(100),
    `Date_reglement` DATE,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `RefPaiement` VARCHAR(20),
    `MontantRegle` INTEGER DEFAULT 0,
    `TypeReglement` VARCHAR(20),
    `IDModePaiement` VARCHAR(10),
    `IDReleveClient` BIGINT,
    `IDClient` BIGINT,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `CreePar` VARCHAR(20),
    `AnnuleOP` TINYINT DEFAULT 0,
    `AnnulePar` VARCHAR(20),
    `SoldeApres` INTEGER DEFAULT 0,
    `SoldeAvant` INTEGER DEFAULT 0,
    `NomBanque` VARCHAR(20),
    `Nom_Ordinateur` NVARCHAR(20),
    `Num_Bande` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Detail_Reglement` (
    `Soldeavant` INTEGER NOT NULL DEFAULT 0,
    `SoldeApres` INTEGER NOT NULL DEFAULT 0,
    `IDDetailReglement` INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `Date_Ajout` DATE NOT NULL,
    `Date_Modif` DATE NOT NULL,
    `Heure_AJout` TIME NOT NULL,
    `Heure_Modif` TIME NOT NULL,
    `DateReglement` DATE NOT NULL,
    `Montantreglement` INTEGER NOT NULL DEFAULT 0,
    `IDReglement` BIGINT NOT NULL,
    `IDFacture` BIGINT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Banque` (
    `IDBanque` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomBanque` VARCHAR(50),
    `NumCompte` VARCHAR(20) DEFAULT '0',
    `IDUtilisateur` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES STOCK / COMMANDE / MOUVEMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS `T_ReleveFournisseur` (
    `IDReleve` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `Date_Edition` DATE,
    `Nomfournisseur` VARCHAR(50),
    `MontantTTC` INTEGER DEFAULT 0,
    `SoldeReleve` INTEGER DEFAULT 0,
    `MontantRegle` INTEGER DEFAULT 0,
    `DateReglement` DATE,
    `IDFournisseur` BIGINT DEFAULT 0,
    `DateReelEdition` DATE,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `RefReleve` VARCHAR(20),
    `DateDebut` DATE,
    `DateFin` DATE,
    `AnnuleOP` TINYINT DEFAULT 0,
    `MontantHT` INTEGER DEFAULT 0,
    `MontantTVA` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_commande` (
    `IDReleve` BIGINT DEFAULT 0,
    `IDCommande` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateCommande` DATE,
    `IDFournisseur` BIGINT DEFAULT 0,
    `MtAchatTTC` INTEGER DEFAULT 0,
    `DateReception` DATE,
    `MtVenteTTC` INTEGER DEFAULT 0,
    `margecommande` INTEGER DEFAULT 0,
    `NumBL` VARCHAR(20),
    `NomFournisseur` VARCHAR(50),
    `IDUtilisateur` BIGINT DEFAULT 0,
    `MAJStock` TINYINT DEFAULT 0,
    `MtAchatTVA` INTEGER DEFAULT 0,
    `MtAchatHT` INTEGER DEFAULT 0,
    `MtVenteHT` INTEGER DEFAULT 0,
    `MtVenteTVA` INTEGER DEFAULT 0,
    `CreePar` VARCHAR(20),
    `ModifiePar` VARCHAR(20),
    `BLSaisiPar` VARCHAR(20),
    `BLValidePar` VARCHAR(20),
    `NbLignes` INTEGER DEFAULT 0,
    `AvoirFour` INTEGER DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `AnnulePar` VARCHAR(20),
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `IDEtatCde` VARCHAR(2),
    `IDUtilisateur_Modif` BIGINT DEFAULT 0,
    `Nom_Ordinateur` NVARCHAR(20),
    `DateDuBL` DATE,
    `EtatCde_Avt_Suppr` VARCHAR(20),
    `IDUtilisateur_annul` INTEGER DEFAULT 0,
    `IDutilisateur_Reception` INTEGER DEFAULT 0,
    `DateAnnul` DATE,
    `IDUtilisateur_ReceptionPartiel` INTEGER DEFAULT 0,
    `DateReceptionPartiel` DATE,
    `HeureCommande` TIME,
    `HeureReception` TIME,
    `HeureReceptionPartiel` TIME,
    `DepotVente` TINYINT DEFAULT 0,
    `Datemodif` DATE,
    `DateAnnulReception` DATE,
    `HeureAnnulReception` TIME,
    `ReceptionAnnulePar` VARCHAR(20),
    `IDUtilisateur_annulReception` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_CommandeLigne` (
    `IDCommandeLigne` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `CodeCIP` VARCHAR(20) DEFAULT '0',
    `IDCommande` BIGINT DEFAULT 0,
    `IDProduit` BIGINT DEFAULT 0,
    `Designation` VARCHAR(50),
    `PUAchatTTC` INTEGER DEFAULT 0,
    `PUVenteTTC` INTEGER DEFAULT 0,
    `TotalAchatTTC` INTEGER DEFAULT 0,
    `TotalVenteTTC` INTEGER DEFAULT 0,
    `IDFournisseur` BIGINT DEFAULT 0,
    `margeligne` INTEGER DEFAULT 0,
    `EtatLigne` VARCHAR(1),
    `Qte_avant` INTEGER DEFAULT 0,
    `qte_Apres` INTEGER DEFAULT 0,
    `Qte_Livree` INTEGER DEFAULT 0,
    `Qte_UG` INTEGER DEFAULT 0,
    `Qte_Cdee` INTEGER DEFAULT 0,
    `PUVenteHT` INTEGER DEFAULT 0,
    `PUAchatHT` INTEGER DEFAULT 0,
    `TauxTVA` SMALLINT DEFAULT 0,
    `DateCommande` DATE,
    `DateReception` DATE,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `DatePeremption` DATE,
    `MAJStock` TINYINT DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `EtatLigne_Avt_Suppr` VARCHAR(1),
    `DepotVente` TINYINT DEFAULT 0,
    `HeureCommande` TIME,
    `HeureReception` TIME,
    `PUPublicHT` INTEGER DEFAULT 0,
    `PUPublicTTC` INTEGER DEFAULT 0,
    `ReferenceProd` VARCHAR(20),
    `NumLot` VARCHAR(20),
    `IDConditionnement` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Mouvement` (
    `IDMouvement` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateMouvement` DATE,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDTypeMvt` VARCHAR(10) DEFAULT '0',
    `IDMotifMvt` VARCHAR(10),
    `AnnuleOP` TINYINT DEFAULT 0,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `CreePar` VARCHAR(20),
    `AnnulePar` VARCHAR(20),
    `Nom_Ordinateur` NVARCHAR(20),
    `NbLignes` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `t_MouvementLigne` (
    `IDDetailMvt` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDMouvement` BIGINT DEFAULT 0,
    `IDProduit` BIGINT DEFAULT 0,
    `CodeCIP` VARCHAR(20),
    `Designation` VARCHAR(50),
    `QteAvant` INTEGER DEFAULT 0,
    `QteApres` INTEGER DEFAULT 0,
    `IDTypeMvt` VARCHAR(10) DEFAULT '0',
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `IDCodeGeo` VARCHAR(10),
    `IDDetailMvt_Traite` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_inventaire` (
    `IDInventaire` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateInventaire` DATE,
    `IDTypeInventaire` VARCHAR(20),
    `IDUtilisateur` BIGINT DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `CreePar` VARCHAR(20),
    `AnnulePar` VARCHAR(20),
    `NbLignes` INTEGER DEFAULT 0,
    `ValideOP` TINYINT DEFAULT 0,
    `ValidePar` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Detail_inventaire` (
    `CodeCIP` VARCHAR(20) DEFAULT '0',
    `Designation` VARCHAR(50),
    `PUAchatTTC` INTEGER DEFAULT 0,
    `PUVenteTTC` INTEGER DEFAULT 0,
    `QteGlobal_Init` INTEGER DEFAULT 0,
    `Traite` TINYINT DEFAULT 0,
    `QteGLobal_Final` INTEGER DEFAULT 0,
    `QteRayon_Final` INTEGER DEFAULT 0,
    `IDDetailInventaire` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDProduit` BIGINT DEFAULT 0,
    `DateAjout` DATE,
    `MAJStock` TINYINT,
    `DateDernierModif` DATE,
    `PUAchatHT` INTEGER DEFAULT 0,
    `PUVenteHT` INTEGER DEFAULT 0,
    `TauxTVA` SMALLINT DEFAULT 0,
    `IDInventaire` BIGINT DEFAULT 0,
    `IDCodeGeo` VARCHAR(10),
    `IDGroupe` VARCHAR(5),
    `IDFamille` BIGINT,
    `IDTypeProduit` VARCHAR(10),
    `IDCategorie` VARCHAR(20),
    `ReferenceProd` VARCHAR(20),
    `EcartRayon` INTEGER DEFAULT 0,
    `DatePeremption` DATE,
    `EcartReserve` INTEGER DEFAULT 0,
    `QteRayon_Init` INTEGER DEFAULT 0,
    `QteReserve_Final` INTEGER DEFAULT 0,
    `EcartGlobal` INTEGER DEFAULT 0,
    `QtePerime` INTEGER DEFAULT 0,
    `Prod_Ajoute` TINYINT DEFAULT 0,
    `QtePremierComptage` INTEGER DEFAULT 0,
    `QteDeuxiemeComptage` INTEGER DEFAULT 0,
    `QteTroisiemeComptage` INTEGER DEFAULT 0,
    `PremierComptageOK` TINYINT DEFAULT 0,
    `DeuxiemeComptageOK` TINYINT DEFAULT 0,
    `TroisiemeComptageOK` TINYINT DEFAULT 0,
    `QteReserve_Init` INTEGER DEFAULT 0,
    `NumLot` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_DepotVente` (
    `IDDepotVente` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `QteDepotVente` INTEGER DEFAULT 0,
    `DateDernierDepot` DATE,
    `DateDerniereVente` DATE,
    `IDClient` BIGINT,
    `IDProduit` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES COMPTABILITE / DEPENSE / JOURNAL
-- ============================================================

CREATE TABLE IF NOT EXISTS `frais_Generaux` (
    `IDCompte` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NumCompte` VARCHAR(20) NOT NULL UNIQUE,
    `Libelle_Frais` VARCHAR(50) NOT NULL,
    `Montant_Prelevement` INTEGER NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Depense` (
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDDepense` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `MotifDepense` VARCHAR(50),
    `MontantDepense` INTEGER DEFAULT 0,
    `DateDepense` DATE,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `AnnuleOP` TINYINT DEFAULT 0,
    `AnnulePar` VARCHAR(20),
    `NumPiece` VARCHAR(20),
    `IDModePaiement` VARCHAR(10),
    `NUM_BANDE` INTEGER DEFAULT 0,
    `NumCompte` VARCHAR(20) UNIQUE,
    `OP_Saisie` INTEGER DEFAULT 0,
    `Beneficiaire` VARCHAR(20),
    `IDCompte` BIGINT,
    `DateModif` DATE,
    `HeureModif` TIME,
    `ModifiePar` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Cloture_Journal` (
    `IDT_Cloture_Journal` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `CABRUT` INTEGER NOT NULL DEFAULT 0,
    `CANET` INTEGER NOT NULL DEFAULT 0,
    `CARemise` INTEGER NOT NULL DEFAULT 0,
    `Carte_de_credits` INTEGER NOT NULL DEFAULT 0,
    `Cheque_comptant` INTEGER NOT NULL DEFAULT 0,
    `Credit_aux_assurances_Mutuelles` INTEGER NOT NULL DEFAULT 0,
    `Credit_particulier` INTEGER NOT NULL DEFAULT 0,
    `Credit_personnel` INTEGER NOT NULL DEFAULT 0,
    `Credit_pharmacien` INTEGER NOT NULL DEFAULT 0,
    `IDUtilisateur` BIGINT NOT NULL DEFAULT 0,
    `Credit_societe` INTEGER NOT NULL DEFAULT 0,
    `Date_operation_jour` DATE NOT NULL,
    `depense` INTEGER NOT NULL DEFAULT 0,
    `ecartcaise` INTEGER NOT NULL DEFAULT 0,
    `Espece_Comptant` INTEGER NOT NULL DEFAULT 0,
    `RATIOJ` REAL NOT NULL DEFAULT 0,
    `Recouvrement_cheques` INTEGER NOT NULL DEFAULT 0,
    `Recouvrements_espece` INTEGER NOT NULL DEFAULT 0,
    `Total_Espece` INTEGER NOT NULL DEFAULT 0,
    `TOTALACHAT` INTEGER NOT NULL DEFAULT 0,
    `totalconst` INTEGER NOT NULL DEFAULT 0,
    `totalcredit` INTEGER NOT NULL DEFAULT 0,
    `totalespeces` INTEGER NOT NULL DEFAULT 0,
    `Virement` INTEGER NOT NULL DEFAULT 0,
    `Marge` BIGINT NOT NULL DEFAULT 0,
    `AnnulationAnt` INTEGER NOT NULL DEFAULT 0,
    `AnnulationJour` INTEGER NOT NULL DEFAULT 0,
    `BASE_TVA1` DOUBLE NOT NULL DEFAULT 0,
    `BASE_TVA2` DOUBLE NOT NULL DEFAULT 0,
    `MT_TVA1` DOUBLE NOT NULL DEFAULT 0,
    `MT_TVA2` DOUBLE NOT NULL DEFAULT 0,
    `IDF_TIROIR` DOUBLE NOT NULL DEFAULT 0,
    `ValeurHTstock` INTEGER NOT NULL DEFAULT 0,
    `Montant_horscaisse` INTEGER NOT NULL DEFAULT 0,
    `Caution_client` INTEGER NOT NULL DEFAULT 0,
    `IDSessionCaisse` BIGINT NOT NULL DEFAULT 0,
    `Credit_depot` INTEGER NOT NULL DEFAULT 0,
    `AutresModereglement` INTEGER NOT NULL DEFAULT 0,
    `CREDITMUGEFCI` INTEGER NOT NULL DEFAULT 0,
    `Montantdeduction` INTEGER NOT NULL DEFAULT 0,
    `PanierMoyen` INTEGER DEFAULT 0,
    `Nbvente` INTEGER DEFAULT 0,
    `BASE_TVA3` DOUBLE DEFAULT 0,
    `MT_TVA3` DOUBLE DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_CTRL_PRIX` (
    `Ancien_PV` INTEGER DEFAULT 0,
    `New_PV` INTEGER DEFAULT 0,
    `IDProduit` BIGINT NOT NULL DEFAULT 0,
    `Ancien_PA` INTEGER DEFAULT 0,
    `New_PA` INTEGER DEFAULT 0,
    `Operateur` INTEGER DEFAULT 0,
    `Date` DATE,
    `Operation` NVARCHAR(25),
    `Heure` TIME,
    `IDCtrlPrix` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Valeur_Journaliere_Stock` (
    `IDValeurJournaliereStock` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `Date_Sauvegarde` DATE,
    `Heure_Sauvegarde` TIME,
    `MtAchat_HT` BIGINT DEFAULT 0,
    `MtAchat_TVA` BIGINT DEFAULT 0,
    `MtAchat_TTC` BIGINT DEFAULT 0,
    `Nom_Ordinateur` NVARCHAR(20),
    `IDUtilisateur` BIGINT DEFAULT 0,
    `Type_Generation` VARCHAR(20),
    `CheminFic` VARCHAR(150),
    `UGAchat_HT` INTEGER DEFAULT 0,
    `UGAchat_TTC` INTEGER DEFAULT 0,
    `UGAchat_TVA` INTEGER DEFAULT 0,
    `UGVente_HT` INTEGER DEFAULT 0,
    `UGVente_TTC` INTEGER DEFAULT 0,
    `UGVente_TVA` INTEGER DEFAULT 0,
    `DateDernierModif` DATE,
    `DateAjout` DATE,
    `MtVente_HT` INTEGER DEFAULT 0,
    `MtVente_TVA` INTEGER DEFAULT 0,
    `MtVente_TTC` BIGINT DEFAULT 0,
    `MtVenteMiniTTC` INTEGER DEFAULT 0,
    `MtVenteMiniHT` INTEGER DEFAULT 0,
    `MtVenteMiniTVA` INTEGER DEFAULT 0,
    `MtPUPublicMiniHT` INTEGER DEFAULT 0,
    `MtPUPublicMiniTVA` INTEGER DEFAULT 0,
    `MtPUPublicMiniTTC` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_DetailSauvegarde` (
    `IDDetailSauvegarde` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDValeurJournaliereStock` BIGINT,
    `IDProduit` BIGINT,
    `Designation` VARCHAR(50),
    `CodeCIP` VARCHAR(20),
    `StockGlobal` INTEGER DEFAULT 0,
    `PUAchatHT` INTEGER DEFAULT 0,
    `PUAchatTTC` INTEGER DEFAULT 0,
    `PUVenteHT` INTEGER DEFAULT 0,
    `PUVenteTTC` INTEGER DEFAULT 0,
    `TauxTVA` SMALLINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES CONNEXION / HISTORIQUE / PARAMS
-- ============================================================

CREATE TABLE IF NOT EXISTS `T_HistoConnexion` (
    `IDHistoConnexion` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateConnexion` DATE,
    `HeureConnexion` TIME,
    `IDUtilisateur` BIGINT,
    `Nom_Ordinateur` NVARCHAR(20),
    `IP_Ordinateur` VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_DetailHistoConnexion` (
    `IDDetailHistoConnexion` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDHistoConnexion` BIGINT,
    `Action` VARCHAR(100),
    `DateAction` DATE,
    `HeureAction` TIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_ConnexionMensuelle` (
    `IDConnexionMensuelle` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateAjout` DATE,
    `HeureAjout` TIME,
    `Nom_Ordinateur` NVARCHAR(20),
    `Nom_Operateur` VARCHAR(20),
    `ActifOP` TINYINT DEFAULT 0,
    `IP_Ordinateur` VARCHAR(20),
    `IDUtilisateur` BIGINT,
    `NbConnexionMois` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_HistoRequete` (
    `IDHistoRequete` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateRequete` DATE,
    `HeureRequete` TIME,
    `RequeteSQL` VARCHAR(1000),
    `IDUtilisateur` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_IDENTITE` (
    `IDIDENTITE` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `NomEntreprise` VARCHAR(100),
    `AdresseEntreprise` VARCHAR(100),
    `TelEntreprise` VARCHAR(30),
    `EmailEntreprise` VARCHAR(50),
    `IDTypeLicence` VARCHAR(1),
    `DateExpiration` DATE,
    `IDUtilisateur` BIGINT,
    `Logo` LONGBLOB,
    `NumContribuable` VARCHAR(30),
    `RC` VARCHAR(30),
    `NumLicence` VARCHAR(30),
    `DateActivation` DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Propiete` (
    `IDPropiete` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `Cle` VARCHAR(30) NOT NULL UNIQUE,
    `ValeurCle` VARCHAR(60) NOT NULL,
    `DateCreation` DATE NOT NULL,
    `IDUtilisateur` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_REQUETES` (
    `PK_REQUETE` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `FONCTION_SQL` NVARCHAR(255),
    `REQUETE_SQL` VARCHAR(1000),
    `TYPE_REQUETE` NVARCHAR(255),
    `TYPE_DATA_DEBUT` DATE,
    `TYPE_DATA_FIN` DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_Conge` (
    `IDConge` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateDebut` DATE,
    `DateFin` DATE,
    `HeureDebut` TIME,
    `HeureFin` TIME,
    `Motif` VARCHAR(50),
    `IDAgent` INTEGER DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `IDUtilisateur_Modif` INTEGER DEFAULT 0,
    `IDUtilisateur_Saisie` INTEGER,
    `DateAjout` TIMESTAMP,
    `DateDernierModif` TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_ContratSigne` (
    `DocContrat` LONGBLOB,
    `IDContratSigne` VARCHAR(20) UNIQUE,
    `NomClient` VARCHAR(100),
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDUtilisateur_modif` BIGINT DEFAULT 0,
    `DateModif` TIMESTAMP,
    `DateEnreg` TIMESTAMP,
    `Code_2ST` VARCHAR(10),
    `IDClient` BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_DetailContrat` (
    `PUVenteTTC` INTEGER DEFAULT 0,
    `Designation` VARCHAR(50),
    `PUVenteHT` INTEGER DEFAULT 0,
    `ProduitActif` TINYINT DEFAULT 0,
    `CreePar` VARCHAR(20),
    `TauxTVA` SMALLINT DEFAULT 0,
    `ModifiePar` VARCHAR(20),
    `ModifieLe` DATE,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDUtilisateur_Modif` BIGINT DEFAULT 0,
    `DateModif` DATE,
    `HeureModif` TIME,
    `IDDetailContrat` INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDProduit` BIGINT,
    `IDContrat` BIGINT,
    `Qte` INTEGER DEFAULT 0,
    `MontantHT` INTEGER DEFAULT 0,
    `MontantTVA` INTEGER DEFAULT 0,
    `MontantTTC` INTEGER DEFAULT 0,
    `NumLigne` INTEGER DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `HeureAjout` TIME,
    `HeureDerniereModif` TIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `T_DetailContrat_Annul` (
    `PUVenteTTC` INTEGER DEFAULT 0,
    `Designation` VARCHAR(50),
    `PUVenteHT` INTEGER DEFAULT 0,
    `ProduitActif` TINYINT DEFAULT 0,
    `CreePar` VARCHAR(20),
    `TauxTVA` SMALLINT DEFAULT 0,
    `ModifiePar` VARCHAR(20),
    `ModifieLe` DATE,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `IDUtilisateur` BIGINT DEFAULT 0,
    `IDUtilisateur_Modif` BIGINT DEFAULT 0,
    `DateModif` DATE,
    `HeureModif` TIME,
    `IDDetailContrat` INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `IDProduit` BIGINT,
    `IDContrat` BIGINT,
    `Qte` INTEGER DEFAULT 0,
    `MontantHT` INTEGER DEFAULT 0,
    `MontantTVA` INTEGER DEFAULT 0,
    `MontantTTC` INTEGER DEFAULT 0,
    `IDUtilisateur_annul` INTEGER DEFAULT 0,
    `DateAnnul` DATE,
    `Nom_Ordinateur` NVARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES PARAMS AVANCEES
-- ============================================================

CREATE TABLE IF NOT EXISTS `T_PARAMS` (
    `OP_UNIQUE` VARCHAR(1) NOT NULL UNIQUE,
    `TVA1` DOUBLE DEFAULT 0,
    `SMS_Au_Proprietaire` TINYINT DEFAULT 0,
    `TVA2` DOUBLE DEFAULT 0,
    `SMS_CLOTURE` TINYINT DEFAULT 0,
    `SMS_CLIENT` TINYINT DEFAULT 0,
    `DEVISE1` DOUBLE DEFAULT 0,
    `DEVISE2` DOUBLE DEFAULT 0,
    `DATE_DERNIERE_OP` TIMESTAMP DEFAULT '1970-01-01 00:00:01',
    `DEVISE1_TXT` VARCHAR(10),
    `DEVISE2_TXT` VARCHAR(10),
    `TVA_DEFAUT` INTEGER DEFAULT 0,
    `FOND_INITIAL` DOUBLE DEFAULT 0,
    `MontantMaxModifVte` INTEGER DEFAULT 0,
    `FOND_FIXE` NVARCHAR(255),
    `BANDE_PAR_JOUR` TINYINT DEFAULT 0,
    `ECART_CAISSE` DOUBLE DEFAULT 0,
    `COFFRE` DOUBLE DEFAULT 0,
    `CHEQUE_HP` NVARCHAR(255),
    `CHEQUE_CTRL` NVARCHAR(255),
    `DEBUT_TICKET` NVARCHAR(255),
    `FIN_TICKET` NVARCHAR(255),
    `ROTA_01` DOUBLE DEFAULT 0,
    `ROTA_02` DOUBLE DEFAULT 0,
    `ROTA_03` DOUBLE DEFAULT 0,
    `ROTA_04` DOUBLE DEFAULT 0,
    `ROTA_05` DOUBLE DEFAULT 0,
    `ROTA_06` DOUBLE DEFAULT 0,
    `ROTA_07` DOUBLE DEFAULT 0,
    `ROTA_08` DOUBLE DEFAULT 0,
    `ROTA_09` DOUBLE DEFAULT 0,
    `ROTA_10` DOUBLE DEFAULT 0,
    `ROTA_11` DOUBLE DEFAULT 0,
    `ROTA_12` DOUBLE DEFAULT 0,
    `POURCENT_GLOBAL` DOUBLE DEFAULT 0,
    `MOIS_ANTICIPATION` DOUBLE DEFAULT 0,
    `MOIS_VARIATION` DOUBLE DEFAULT 0,
    `POURCENT_ANTICIPATION` DOUBLE DEFAULT 0,
    `POURCENT_VARIATION` DOUBLE DEFAULT 0,
    `MINI_ANNUEL` DOUBLE DEFAULT 0,
    `MINI_STOCK_SEUL` NVARCHAR(255),
    `POURCENT_MINI` DOUBLE DEFAULT 0,
    `LIBEL_CHEQUE` VARCHAR(255),
    `SMS_LANCEMENT` TINYINT DEFAULT 0,
    `PC_UNIT_ACHAT` SMALLINT DEFAULT 0,
    `VERSION` VARCHAR(20),
    `TXT_FIN_FAC` NVARCHAR(255),
    `INFO_OP` NVARCHAR(255),
    `NomSurEtiquette` TINYINT DEFAULT 0,
    `VERIF_MONTANT` DOUBLE DEFAULT 0,
    `VERIF_QTE` DOUBLE DEFAULT 0,
    `ECART_ENCOURS_MAXI` DOUBLE DEFAULT 0,
    `CAISSE_PAR_TIROIR` TINYINT DEFAULT 0,
    `NOM_DEVISE` TINYINT DEFAULT 0,
    `REMISE_AUTO` TINYINT DEFAULT 0,
    `LIMITE_CHEQUE` DOUBLE DEFAULT 0,
    `SMS_BIELLETAGE` TINYINT DEFAULT 0,
    `VERIF_PRIX` TINYINT DEFAULT 0,
    `DOUBLE_TICKET` TINYINT DEFAULT 0,
    `MAJ_RESERVE_EN_RECEP` TINYINT DEFAULT 0,
    `VERIF_FAMILLES` TINYINT DEFAULT 0,
    `Nb_Produits` TINYINT DEFAULT 0,
    `VERIF_VENDEUR` TINYINT DEFAULT 0,
    `DESIGNATION_SUR_UNE_LIGNE` TINYINT DEFAULT 0,
    `Texte_condition_commerciale` VARCHAR(200),
    `Code_Deblocage` VARCHAR(8),
    `Periode_mini` INTEGER DEFAULT 0,
    `PeriodeMaxi` INTEGER DEFAULT 0,
    `UnitMini` VARCHAR(50) DEFAULT '0',
    `UnitMaxi` VARCHAR(50),
    `UnitAlerte` VARCHAR(50),
    `PriodeAlerte` INTEGER DEFAULT 0,
    `DateMiseAJour` TIMESTAMP DEFAULT '1970-01-01 00:00:01',
    `CIPDEFAUT` VARCHAR(7) DEFAULT '0',
    `Decondition_Auto` TINYINT DEFAULT 0,
    `GESTION_HC` TINYINT DEFAULT 0,
    `TAUX_REDUCTION_CA` REAL DEFAULT 0,
    `PERIODE_COUVERTURE` INTEGER DEFAULT 0,
    `UNITCOUVERTURE` VARCHAR(50),
    `Afficher_remise` TINYINT DEFAULT 1,
    `Multi_vendeur` TINYINT DEFAULT 0,
    `TAUX_BIC` REAL DEFAULT 0,
    `Caisse_par_session` TINYINT DEFAULT 0,
    `MAJ_PRIX_CMDE` TINYINT DEFAULT 1,
    `MODIF_AUTO_COEF` TINYINT DEFAULT 1,
    `Control_peremption` TINYINT DEFAULT 0,
    `NumFactManuel` TINYINT DEFAULT 0,
    `DepensePetiteCaisse` TINYINT DEFAULT 0,
    `EnPromo` TINYINT DEFAULT 0,
    `TauxPromotion` INTEGER DEFAULT 0,
    `TAUXASSURANCE` INTEGER DEFAULT 0,
    `GestEtablissementPrincipalCmde` TINYINT DEFAULT 0,
    `EnregistrerDernierPrixDeVente` TINYINT DEFAULT 1,
    `ActiverGestionStock` TINYINT DEFAULT 0,
    `ActiverGestionVente` TINYINT DEFAULT 0,
    `Chemin_Sauvegarde` VARCHAR(100),
    `ActiverGestionContrat` TINYINT DEFAULT 0,
    `ActiverGestionJournal` TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLES WEB (W_*)
-- ============================================================

CREATE TABLE IF NOT EXISTS `W_Commande` (
    `IDReleve` BIGINT DEFAULT 0,
    `IDCommande` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateCommande` DATE,
    `IDFournisseur` BIGINT DEFAULT 0,
    `MtAchatTTC` INTEGER DEFAULT 0,
    `DateReception` DATE,
    `MtVenteTTC` INTEGER DEFAULT 0,
    `margecommande` INTEGER DEFAULT 0,
    `NumBL` VARCHAR(20),
    `NomFournisseur` VARCHAR(50),
    `IDUtilisateur` BIGINT DEFAULT 0,
    `MAJStock` TINYINT DEFAULT 0,
    `MtAchatTVA` INTEGER DEFAULT 0,
    `MtAchatHT` INTEGER DEFAULT 0,
    `MtVenteHT` INTEGER DEFAULT 0,
    `MtVenteTVA` INTEGER DEFAULT 0,
    `CreePar` VARCHAR(20),
    `ModifiePar` VARCHAR(20),
    `BLSaisiPar` VARCHAR(20),
    `BLValidePar` VARCHAR(20),
    `NbLignes` INTEGER DEFAULT 0,
    `AvoirFour` INTEGER DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `AnnulePar` VARCHAR(20),
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `IDEtatCde` VARCHAR(2),
    `IDUtilisateur_Modif` BIGINT DEFAULT 0,
    `Nom_Ordinateur` NVARCHAR(20),
    `DateDuBL` DATE,
    `EtatCde_Avt_Suppr` VARCHAR(20),
    `IDUtilisateur_annul` INTEGER DEFAULT 0,
    `IDutilisateur_Reception` INTEGER DEFAULT 0,
    `DateAnnul` DATE,
    `IDUtilisateur_ReceptionPartiel` INTEGER DEFAULT 0,
    `DateReceptionPartiel` DATE,
    `HeureCommande` TIME,
    `HeureReception` TIME,
    `HeureReceptionPartiel` TIME,
    `DepotVente` TINYINT DEFAULT 0,
    `Datemodif` DATE,
    `DateAnnulReception` DATE,
    `HeureAnnulReception` TIME,
    `ReceptionAnnulePar` VARCHAR(20),
    `IDUtilisateur_annulReception` INTEGER DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `W_CommandeLigne` (
    `IDCommandeLigne` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `codeCIP` VARCHAR(20) DEFAULT '0',
    `IDCommande` BIGINT DEFAULT 0,
    `IDProduit` BIGINT DEFAULT 0,
    `Designation` VARCHAR(50),
    `PUAchatTTC` INTEGER DEFAULT 0,
    `PUVenteTTC` INTEGER DEFAULT 0,
    `TotalAchatTTC` INTEGER DEFAULT 0,
    `TotalVenteTTC` INTEGER DEFAULT 0,
    `IDFournisseur` BIGINT DEFAULT 0,
    `margeligne` INTEGER DEFAULT 0,
    `EtatLigne` VARCHAR(1),
    `Qte_avant` INTEGER DEFAULT 0,
    `qte_Apres` INTEGER DEFAULT 0,
    `Qte_Livree` INTEGER DEFAULT 0,
    `Qte_UG` INTEGER DEFAULT 0,
    `Qte_Cdee` INTEGER DEFAULT 0,
    `PUVenteHT` INTEGER DEFAULT 0,
    `PUAchatHT` INTEGER DEFAULT 0,
    `TauxTVA` SMALLINT DEFAULT 0,
    `DateCommande` DATE,
    `DateReception` DATE,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `DatePeremption` DATE,
    `MAJStock` TINYINT DEFAULT 0,
    `AnnuleOP` TINYINT DEFAULT 0,
    `EtatLigne_Avt_Suppr` VARCHAR(1),
    `DepotVente` TINYINT DEFAULT 0,
    `HeureCommande` TIME,
    `HeureReception` TIME,
    `PUPublicHT` INTEGER DEFAULT 0,
    `PUPublicTTC` INTEGER DEFAULT 0,
    `ReferenceProd` VARCHAR(20),
    `NumLot` VARCHAR(20),
    `Nom_Ordinateur` NVARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `W_lignes` (
    `IDLigne` BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `DateFacture` DATE,
    `IDFacture` BIGINT DEFAULT 0,
    `TotalMargeLigne` INTEGER DEFAULT 0,
    `TotalAchatTTC` INTEGER DEFAULT 0,
    `TotalVenteTTC` INTEGER DEFAULT 0,
    `Designation` VARCHAR(50),
    `PUAchatTTC` INTEGER DEFAULT 0,
    `PUVenteTTC` INTEGER DEFAULT 0,
    `QteStock_Avant` INTEGER DEFAULT 0,
    `QteStock_Apres` INTEGER DEFAULT 0,
    `PUVenteHT` INTEGER,
    `Qte_Vendu` INTEGER DEFAULT 0,
    `IDProduit` BIGINT DEFAULT 0,
    `DateAjout` DATE,
    `DateDernierModif` DATE,
    `PUAchatHT` INTEGER DEFAULT 0,
    `TauxTVA` SMALLINT DEFAULT 0,
    `IDCodeGeo` VARCHAR(10),
    `AnnuleOP` TINYINT DEFAULT 0,
    `TotalAchatHT` INTEGER DEFAULT 0,
    `TotalVenteHT` INTEGER DEFAULT 0,
    `TauxRemise` SMALLINT DEFAULT 0,
    `TotalRemise` INTEGER DEFAULT 0,
    `TotalVenteTVA` INTEGER DEFAULT 0,
    `NumLigne` INTEGER DEFAULT 0,
    `CodeCIP` VARCHAR(20),
    `ReferenceProd` VARCHAR(20),
    `IDGroupe` VARCHAR(5),
    `CODE_VENTIL_CA` BIGINT,
    `Nom_Ordinateur` NVARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
