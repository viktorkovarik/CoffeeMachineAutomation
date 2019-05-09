
-- Dumping structure for table pds.action
CREATE TABLE IF NOT EXISTS `action` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` varchar(50) NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- Dumping structure for table pds.consumption
CREATE TABLE IF NOT EXISTS `consumption` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` int(10) unsigned NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Dumping structure for table pds.emptywater
CREATE TABLE IF NOT EXISTS `emptywater` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
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

-- Dumping structure for table coffeeesp.user_list
CREATE TABLE IF NOT EXISTS `user_list` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cardID` int(10) unsigned NOT NULL DEFAULT '0',
  `username` varchar(50) DEFAULT NULL,
  `enabled` tinyint(1) unsigned DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `cardID` (`cardID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Dumping structure for table coffeeesp.last_refill
CREATE TABLE IF NOT EXISTS `last_refill` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `val` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- init refill time
INSERT INTO last_refill(val) VALUES (1); 