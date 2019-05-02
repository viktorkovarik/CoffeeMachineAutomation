CREATE DATABASE IF NOT EXISTS `pds` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `pds`;

-- Dumping structure for table pds.action
CREATE TABLE IF NOT EXISTS `action` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` varchar(50) NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Dumping structure for table pds.consumption
CREATE TABLE IF NOT EXISTS `consumption` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` int(10) unsigned NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Dumping structure for table pds.emptywater
CREATE TABLE IF NOT EXISTS `emptywater` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Dumping structure for table pds.power_on
CREATE TABLE IF NOT EXISTS `power_on` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Dumping structure for table pds.readcard
CREATE TABLE IF NOT EXISTS `readcard` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` int(10) unsigned NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Dumping structure for table pds.ready
CREATE TABLE IF NOT EXISTS `ready` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Dumping structure for table pds.user_list
CREATE TABLE IF NOT EXISTS `user_list` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `cardID` int(10) unsigned NOT NULL DEFAULT '0',
  `username` varchar(50) DEFAULT NULL,
  `enabled` tinyint(1) unsigned DEFAULT '1',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
