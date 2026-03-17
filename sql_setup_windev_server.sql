-- ================================================================
-- SCRIPT À EXÉCUTER SUR LE SERVEUR MySQL WINDEV
-- Ce script prépare MySQL pour accepter les connexions
-- depuis le VPS Django (application web SAV Pharmacie)
-- ================================================================

-- Remplacer 'IP_DU_VPS' par l'IP publique réelle de votre VPS Django
-- Remplacer les mots de passe par des mots de passe forts

-- ────────────────────────────────────────────────────
-- 1. Créer la base de données pour Django
-- ────────────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS `sav_pharmacie`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- ────────────────────────────────────────────────────
-- 2. Créer l'utilisateur Django (lecture/écriture sur sav_pharmacie)
--    Accessible uniquement depuis l'IP du VPS
-- ────────────────────────────────────────────────────
CREATE USER IF NOT EXISTS 'sav_app'@'IP_DU_VPS'
    IDENTIFIED BY 'MOT_DE_PASSE_FORT_ICI';

GRANT ALL PRIVILEGES ON `sav_pharmacie`.* TO 'sav_app'@'IP_DU_VPS';

-- ────────────────────────────────────────────────────
-- 3. Créer l'utilisateur de synchronisation bidirectionnelle
--    Django lit TOUTES les tables WinDev (SELECT)
--    Django écrit UNIQUEMENT dans les tables de sync (INSERT/UPDATE)
-- ────────────────────────────────────────────────────
CREATE USER IF NOT EXISTS 'sav_sync'@'IP_DU_VPS'
    IDENTIFIED BY 'MOT_DE_PASSE_SYNC_ICI';

-- Lecture sur toute la base WinDev
GRANT SELECT ON `FacturationClient`.* TO 'sav_sync'@'IP_DU_VPS';

-- Écriture limitée aux tables de synchronisation Django → WinDev
GRANT INSERT, UPDATE ON `FacturationClient`.`T_BesoinsClient`
    TO 'sav_sync'@'IP_DU_VPS';
GRANT INSERT, UPDATE ON `FacturationClient`.`T_DetailIntervention`
    TO 'sav_sync'@'IP_DU_VPS';

-- ────────────────────────────────────────────────────
-- 4. Appliquer les privilèges
-- ────────────────────────────────────────────────────
FLUSH PRIVILEGES;

-- ────────────────────────────────────────────────────
-- 5. IMPORTANT : Configurer MySQL pour accepter les connexions distantes
--
--    Dans le fichier my.cnf (ou my.ini sous Windows) du serveur WinDev :
--
--    [mysqld]
--    bind-address = 0.0.0.0
--
--    Puis redémarrer MySQL :
--    - Windows : net stop mysql && net start mysql
--    - Linux   : sudo systemctl restart mysql
--
-- 6. FIREWALL : Ouvrir le port 3306 uniquement pour l'IP du VPS
--
--    Windows Firewall (PowerShell admin) :
--    netsh advfirewall firewall add rule name="MySQL VPS SAV" ^
--        dir=in action=allow protocol=TCP localport=3306 ^
--        remoteip=IP_DU_VPS
--
--    Linux (ufw) :
--    sudo ufw allow from IP_DU_VPS to any port 3306
--
-- ────────────────────────────────────────────────────

-- ================================================================
-- VÉRIFICATION : tester depuis le VPS avec :
--   mysql -h IP_SERVEUR_WINDEV -u sav_app -p sav_pharmacie
--   mysql -h IP_SERVEUR_WINDEV -u sav_sync -p FacturationClient
-- ================================================================
