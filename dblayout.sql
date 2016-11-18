-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server Version:               5.7.16-log - MySQL Community Server (GPL)
-- Server Betriebssystem:        Win64
-- HeidiSQL Version:             9.4.0.5125
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- Exportiere Struktur von Tabelle mcdatadump.dimensionref
CREATE TABLE IF NOT EXISTS `dimensionref` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DimName` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- Daten Export vom Benutzer nicht ausgewählt
-- Exportiere Struktur von Tabelle mcdatadump.graves
CREATE TABLE IF NOT EXISTS `graves` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `playerID` int(11) NOT NULL,
  `graveDim` int(11) NOT NULL,
  `graveFullPath` text NOT NULL,
  `gravedata` json NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK_graves_mcuserprofiles` (`playerID`),
  KEY `FK_graves_dimensionref` (`graveDim`),
  CONSTRAINT `FK_graves_dimensionref` FOREIGN KEY (`graveDim`) REFERENCES `dimensionref` (`ID`),
  CONSTRAINT `FK_graves_mcuserprofiles` FOREIGN KEY (`playerID`) REFERENCES `mcuserprofiles` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Daten Export vom Benutzer nicht ausgewählt
-- Exportiere Struktur von Tabelle mcdatadump.itemref
CREATE TABLE IF NOT EXISTS `itemref` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ItemID` int(11) NOT NULL DEFAULT '0',
  `Name` text NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=8192 DEFAULT CHARSET=utf8;

-- Daten Export vom Benutzer nicht ausgewählt
-- Exportiere Struktur von Tabelle mcdatadump.mcprofiles
CREATE TABLE IF NOT EXISTS `mcprofiles` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `playerID` int(11) NOT NULL,
  `PlayerDat` json NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK_mcjsondata_mcuserprofiles` (`playerID`),
  CONSTRAINT `FK_mcjsondata_mcuserprofiles` FOREIGN KEY (`playerID`) REFERENCES `mcuserprofiles` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Daten Export vom Benutzer nicht ausgewählt
-- Exportiere Struktur von Tabelle mcdatadump.mcstats
CREATE TABLE IF NOT EXISTS `mcstats` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `playerID` int(11) NOT NULL,
  `statsJson` json NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `FK__mcuserprofiles` (`playerID`),
  CONSTRAINT `FK__mcuserprofiles` FOREIGN KEY (`playerID`) REFERENCES `mcuserprofiles` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Daten Export vom Benutzer nicht ausgewählt
-- Exportiere Struktur von Tabelle mcdatadump.mcuserprofiles
CREATE TABLE IF NOT EXISTS `mcuserprofiles` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `UUID` varchar(36) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `UUID` (`UUID`)
) ENGINE=InnoDB AUTO_INCREMENT=1797 DEFAULT CHARSET=utf8;

-- Daten Export vom Benutzer nicht ausgewählt
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
