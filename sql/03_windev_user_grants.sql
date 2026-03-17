-- Creation de l'utilisateur sav_sync et attribution des droits
-- Execute apres 01 et 02

-- Creer l'utilisateur
CREATE USER IF NOT EXISTS 'sav_sync'@'127.0.0.1' IDENTIFIED BY 'sav_sync_2024!';
CREATE USER IF NOT EXISTS 'sav_sync'@'localhost' IDENTIFIED BY 'sav_sync_2024!';

-- Lecture sur toute la base WinDev
GRANT SELECT ON `FacturationClient`.* TO 'sav_sync'@'127.0.0.1';
GRANT SELECT ON `FacturationClient`.* TO 'sav_sync'@'localhost';

-- Ecriture limitee aux tables de sync bidirectionnelle
GRANT INSERT, UPDATE ON `FacturationClient`.`T_BesoinsClient` TO 'sav_sync'@'127.0.0.1';
GRANT INSERT, UPDATE ON `FacturationClient`.`T_BesoinsClient` TO 'sav_sync'@'localhost';
GRANT INSERT, UPDATE ON `FacturationClient`.`T_DetailIntervention` TO 'sav_sync'@'127.0.0.1';
GRANT INSERT, UPDATE ON `FacturationClient`.`T_DetailIntervention` TO 'sav_sync'@'localhost';

FLUSH PRIVILEGES;
