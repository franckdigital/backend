-- Donnees de reference et de test pour FacturationClient
-- Execute apres 01_windev_schema_tables.sql

SET NAMES utf8mb4;

-- ============================================================
-- DONNEES DE REFERENCE
-- ============================================================

INSERT INTO T_TypeIntervention (IDTypeIntervention, LibTypeIntervention) VALUES
('MAINT', 'Maintenance preventive'),
('DEPAN', 'Depannage / Reparation'),
('INSTAL', 'Installation'),
('FORMAT', 'Formation'),
('INVENT', 'Inventaire'),
('AUDIT', 'Audit technique');

INSERT INTO T_Ville (IDVille, NomVille) VALUES
(1, 'Abidjan'),
(2, 'Bouake'),
(3, 'Daloa'),
(4, 'Yamoussoukro'),
(5, 'San Pedro'),
(6, 'Korhogo'),
(7, 'Man');

INSERT INTO T_Localite (IDLocalite, NomLocalite, IDVille) VALUES
(1, 'Cocody', 1),
(2, 'Plateau', 1),
(3, 'Marcory', 1),
(4, 'Yopougon', 1),
(5, 'Treichville', 1),
(6, 'Adjame', 1),
(7, 'Abobo', 1),
(8, 'Centre-ville Bouake', 2),
(9, 'Centre-ville Daloa', 3),
(10, 'Centre-ville Yamoussoukro', 4),
(11, 'Port-Bouet', 1),
(12, 'Koumassi', 1);

INSERT INTO T_Nature (IDNature, LibNature) VALUES
(1, 'Probleme logiciel'),
(2, 'Probleme materiel'),
(3, 'Mise a jour'),
(4, 'Configuration reseau'),
(5, 'Sauvegarde donnees'),
(6, 'Formation utilisateur');

INSERT INTO T_ProfilUtilisateur (IDProfil, NomProfil, DescriptionProfil, ActifOP) VALUES
('ADMIN', 'Administrateur', 'Acces complet au systeme', 1),
('TECH', 'Technicien', 'Technicien SAV', 1),
('VENTE', 'Vendeur', 'Gestion des ventes', 1),
('CAISSE', 'Caissier', 'Gestion de la caisse', 1);

INSERT INTO T_ModePaiement (IDModePaiement, LibModePaiement) VALUES
('ESP', 'Especes'),
('CHQ', 'Cheque'),
('VIR', 'Virement'),
('CB', 'Carte bancaire'),
('OM', 'Orange Money'),
('MOMO', 'MTN Money'),
('MOOV', 'Moov Money');

INSERT INTO T_EtatCommande (IDEtatCde, LibEtatCde) VALUES
('EN', 'En cours'),
('VA', 'Validee'),
('RE', 'Receptionnee'),
('AN', 'Annulee'),
('RP', 'Reception partielle');

INSERT INTO T_TypeMvt (IDTypeMvt, LibtypeMvt) VALUES
('ENT', 'Entree'),
('SOR', 'Sortie'),
('RET', 'Retour fournisseur'),
('DEC', 'Deconditionnement'),
('PER', 'Perime');

INSERT INTO T_TypeProduit (IDTypeProduit, LibTypeProduit) VALUES
('MED', 'Medicament'),
('PARA', 'Parapharmacie'),
('DISP', 'Dispositif medical'),
('COSM', 'Cosmetique'),
('COMP', 'Complement alimentaire');

INSERT INTO T_TVA (TauxTVA, FNE_TypeTaxe, FNE_DescriptionTypeTxe) VALUES
(0, 'EXO', 'Exonere'),
(9, 'RED', 'Taux reduit'),
(18, 'NOR', 'Taux normal');

INSERT INTO T_Sexe (IDSexe, LibSexe) VALUES
('M', 'Masculin'),
('F', 'Feminin');

INSERT INTO T_Civilite (IDCivilite, LibCivilite) VALUES
('M.', 'Monsieur'),
('Mme', 'Madame'),
('Dr', 'Docteur'),
('Pr', 'Professeur');

INSERT INTO T_TypeClient (IDTypeClient, LibTypeClient) VALUES
('PHARMA', 'Pharmacie'),
('CLINIQ', 'Clinique'),
('HOPIT', 'Hopital'),
('LABO', 'Laboratoire');

INSERT INTO T_PeriodiciteContrat (IDPeriodiciteContrat, LibPeriodiciteContrat, NbJoursPeriode) VALUES
('MENS', 'Mensuelle', 30),
('TRIM', 'Trimestrielle', 90),
('SEM', 'Semestrielle', 180),
('ANN', 'Annuelle', 365);

INSERT INTO T_TypeContrat (IDTypeContrat, LibTypeContrat) VALUES
(1, 'Maintenance'),
(2, 'Support'),
(3, 'Licence');

INSERT INTO T_TypeLicence (IDTypeLicence, LibTypeLicence) VALUES
('S', 'Standard'),
('P', 'Premium'),
('E', 'Enterprise');

INSERT INTO T_Nature_TypeIntervention (IDNature_TypeIntervention, IDTypeIntervention, IDNature) VALUES
(1, 'MAINT', 1),
(2, 'MAINT', 2),
(3, 'MAINT', 3),
(4, 'DEPAN', 1),
(5, 'DEPAN', 2),
(6, 'FORMAT', 6);

-- ============================================================
-- DONNEES DE TEST - UTILISATEURS (Techniciens)
-- ============================================================

INSERT INTO T_Utilisateur (IDUtilisateur, CodeUtilisateur, NomComplet, TelCel, telCel2,
    ActifOP, AccesApplication, Technicien, Disponible, IDProfil,
    DateAjout, DateDernierModif) VALUES
(1, 'ADMIN01', 'Kouame Jean-Pierre', '0707010101', NULL,
    1, 1, 0, 1, 'ADMIN',
    '2024-01-01', '2024-01-01'),
(2, 'TECH01', 'Kone Moussa', '0707020202', '0505020202',
    1, 1, 1, 1, 'TECH',
    '2024-01-15', '2024-06-01'),
(3, 'TECH02', 'Diallo Amadou', '0707030303', '0505030303',
    1, 1, 1, 1, 'TECH',
    '2024-02-01', '2024-06-01'),
(4, 'TECH03', 'Toure Ibrahim', '0707040404', NULL,
    1, 1, 1, 0, 'TECH',
    '2024-03-01', '2024-06-01'),
(5, 'TECH04', 'Bamba Sekou', '0707050505', '0505050505',
    1, 1, 1, 1, 'TECH',
    '2024-03-15', '2024-07-01'),
(6, 'TECH05', 'Ouattara Drissa', '0707060606', NULL,
    0, 1, 1, 0, 'TECH',
    '2024-04-01', '2024-08-01');

-- ============================================================
-- DONNEES DE TEST - CLIENTS (Pharmacies)
-- ============================================================

INSERT INTO T_Client (IDClient, NomClient, TelFixe, TelCel, Code_2ST,
    AdresseGeo, EmailClient, NomResponsable, TelPharmacien,
    SousContrat, IDLocalite, ActifOP, InterieurPays,
    DateMaintenance, MontantContrat, telCel2,
    DateAjout, DateDernierModif, IDTypeClient) VALUES
(1, 'Pharmacie du Plateau', '27200101', '0707101010', 'PL01',
    'Rue du Commerce, Plateau', 'plateau@pharma.ci', 'Dr Kouassi Marie', '0707111111',
    1, 2, 1, 0,
    '2024-12-15', 500000, '0505111111',
    '2024-01-10', '2024-06-01', 'PHARMA'),
(2, 'Pharmacie Sainte-Anne', '27200202', '0707202020', 'SA02',
    'Bd Lagunaire, Cocody', 'ste.anne@pharma.ci', 'Dr Aka Philippe', '0707222222',
    1, 1, 1, 0,
    '2025-01-20', 600000, NULL,
    '2024-02-05', '2024-07-01', 'PHARMA'),
(3, 'Pharmacie de la Paix', '27200303', '0707303030', 'PX03',
    'Marche de Marcory', 'paix@pharma.ci', 'Dr Ble Suzanne', '0707333333',
    1, 3, 1, 0,
    '2025-03-10', 450000, '0505333333',
    '2024-03-12', '2024-08-01', 'PHARMA'),
(4, 'Pharmacie Yopougon-Sante', '27200404', '0707404040', 'YS04',
    'Carrefour Yopougon', 'yopsante@pharma.ci', 'Dr N''Guessan Alain', '0707444444',
    0, 4, 1, 0,
    NULL, 0, NULL,
    '2024-04-20', '2024-09-01', 'PHARMA'),
(5, 'Pharmacie Bouake-Centre', '27300505', '0707505050', 'BC05',
    'Avenue Houphouet, Bouake', 'bouake@pharma.ci', 'Dr Coulibaly Fatou', '0707555555',
    1, 8, 1, 1,
    '2025-06-01', 400000, NULL,
    '2024-05-01', '2024-10-01', 'PHARMA'),
(6, 'Pharmacie Daloa Moderne', '27320606', '0707606060', 'DM06',
    'Centre commercial, Daloa', 'daloa@pharma.ci', 'Dr Tra Bi Paul', '0707666666',
    1, 9, 1, 1,
    '2025-04-15', 350000, '0505666666',
    '2024-06-01', '2024-11-01', 'PHARMA'),
(7, 'Pharmacie Treichville-Port', '27210707', '0707707070', 'TP07',
    'Pres du port, Treichville', 'treich@pharma.ci', 'Dr Zadi Germaine', '0707777777',
    0, 5, 0, 0,
    NULL, 0, NULL,
    '2024-07-01', '2024-12-01', 'PHARMA'),
(8, 'Pharmacie Adjame-Marche', '27200808', '0707808080', 'AM08',
    'Marche Adjame', 'adjame@pharma.ci', 'Dr Soro Adama', '0707888888',
    1, 6, 1, 0,
    '2025-02-28', 500000, NULL,
    '2024-08-01', '2025-01-01', 'PHARMA');

-- ============================================================
-- DONNEES DE TEST - INTERVENTIONS
-- ============================================================

INSERT INTO T_Intervention (IDIntervention, DateIntervention, IDClient, IDTypeIntervention,
    IDUtilisateur, IDIntervention2emeUtilisateur, ValideOP, AnnuleOP, EffectueOP,
    NbJours, DateChoisie, DateChoisieFin, MontantTTC, Frais_Technicien,
    DateAjout, DateDernierModif) VALUES
(1, '2025-01-10', 1, 'MAINT', 2, 0, 1, 0, 1,
    1, '2025-01-10', '2025-01-10', 50000, 15000,
    '2025-01-05', '2025-01-10'),
(2, '2025-01-20', 2, 'DEPAN', 3, 0, 1, 0, 1,
    1, '2025-01-20', '2025-01-20', 75000, 20000,
    '2025-01-18', '2025-01-20'),
(3, '2025-02-05', 3, 'INSTAL', 2, 5, 1, 0, 1,
    2, '2025-02-05', '2025-02-06', 150000, 40000,
    '2025-02-01', '2025-02-06'),
(4, '2025-02-15', 5, 'MAINT', 5, 0, 1, 0, 1,
    1, '2025-02-15', '2025-02-15', 50000, 25000,
    '2025-02-10', '2025-02-15'),
(5, '2025-03-01', 1, 'DEPAN', 2, 0, 1, 0, 0,
    1, '2025-03-01', '2025-03-01', 60000, 15000,
    '2025-02-28', '2025-03-01'),
(6, '2025-03-10', 4, 'FORMAT', 3, 0, 1, 0, 0,
    2, '2025-03-10', '2025-03-11', 100000, 30000,
    '2025-03-05', '2025-03-10'),
(7, '2025-03-15', 6, 'INVENT', 5, 2, 1, 0, 0,
    3, '2025-03-15', '2025-03-17', 200000, 50000,
    '2025-03-10', '2025-03-15'),
(8, '2025-01-05', 8, 'DEPAN', 4, 0, 1, 1, 0,
    1, '2025-01-05', '2025-01-05', 40000, 10000,
    '2025-01-03', '2025-01-05');

-- ============================================================
-- DONNEES DE TEST - BESOINS CLIENT
-- ============================================================

INSERT INTO T_BesoinsClient (IDBesoinsClient, DateBesoin, DescriptionBesoin,
    ValideOP, Traite, Annule, IDClient, IDUtilisateur, NomTechnicien) VALUES
(1, '2025-01-08', 'Mise a jour logiciel MagicSuite vers version 5.2',
    1, 1, 0, 1, 2, 'Kone Moussa'),
(2, '2025-01-15', 'Installation imprimante ticket de caisse',
    1, 1, 0, 2, 3, 'Diallo Amadou'),
(3, '2025-02-01', 'Probleme connexion serveur base de donnees',
    1, 0, 0, 3, 2, 'Kone Moussa'),
(4, '2025-02-20', 'Formation nouveau personnel sur module ventes',
    0, 0, 0, 5, 0, NULL),
(5, '2025-03-01', 'Sauvegarde complete avant inventaire annuel',
    1, 0, 0, 6, 5, 'Bamba Sekou');

-- ============================================================
-- DONNEES DE TEST - DETAIL INTERVENTION
-- ============================================================

INSERT INTO T_DetailIntervention (IDDetailIntervention, IDIntervention, IDNature,
    DescriptionDetail, IDUtilisateur) VALUES
(1, 1, 3, 'Mise a jour MagicSuite 5.1 vers 5.2. Verification des modules facturation et stock.', 2),
(2, 1, 1, 'Correction bug affichage des soldes clients negatifs.', 2),
(3, 2, 2, 'Remplacement disque dur serveur - migration donnees.', 3),
(4, 3, 1, 'Installation complete MagicSuite sur nouveau serveur. Configuration reseau.', 2),
(5, 3, 4, 'Configuration connexion entre postes clients et serveur principal.', 5),
(6, 4, 3, 'Maintenance preventive semestrielle - verification integrite base de donnees.', 5),
(7, 5, 1, 'Diagnostic probleme lenteur module caisse - optimisation requetes.', 2);

-- ============================================================
-- DONNEES DE TEST - PRODUITS (quelques exemples)
-- ============================================================

INSERT INTO T_produit (IDProduit, CodeCIP, Designation, PUAchatTTC, PUVenteTTC,
    PUAchatHT, PUVenteHT, TauxTVA, StockGlobal, ProduitActif,
    IDTypeProduit, DateAjout, DateDernierModif) VALUES
(1, '3400001', 'Paracetamol 500mg', 800, 1200, 672, 1008, 18, 500, 1, 'MED', '2024-01-01', '2025-01-01'),
(2, '3400002', 'Amoxicilline 500mg', 2500, 3800, 2100, 3192, 18, 200, 1, 'MED', '2024-01-01', '2025-01-01'),
(3, '3400003', 'Ibuprofene 400mg', 1000, 1500, 840, 1260, 18, 350, 1, 'MED', '2024-01-01', '2025-01-01'),
(4, '3400004', 'Vitamine C 1000mg', 1500, 2500, 1380, 2300, 9, 150, 1, 'COMP', '2024-03-01', '2025-01-01'),
(5, '3400005', 'Gel hydroalcoolique 500ml', 2000, 3000, 1680, 2520, 18, 100, 1, 'PARA', '2024-06-01', '2025-01-01');

-- ============================================================
-- DONNEES DE TEST - IDENTITE ENTREPRISE
-- ============================================================

INSERT INTO T_IDENTITE (IDIDENTITE, NomEntreprise, AdresseEntreprise, TelEntreprise,
    EmailEntreprise, IDTypeLicence) VALUES
(1, '2ST - Services et Solutions Techniques', 'Abidjan, Cocody Angre', '27 22 00 00 00',
    'contact@2st.ci', 'P');

-- PARAMS de base
INSERT INTO T_PARAMS (OP_UNIQUE, VERSION, DEVISE1_TXT, TVA_DEFAUT) VALUES
('1', '5.2.0', 'FCFA', 18);
