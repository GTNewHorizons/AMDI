-- phpMyAdmin SQL Dump
-- version 4.6.4
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Erstellungszeit: 21. Nov 2016 um 12:13
-- Server-Version: 5.7.16
-- PHP-Version: 5.6.27-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Datenbank: `mcdata`
--

DELIMITER $$
--
-- Prozeduren
--
DROP PROCEDURE IF EXISTS `show_graves_for_player`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `show_graves_for_player` (IN `playerName` VARCHAR(50) CHARSET utf8, IN `playerUUID` VARCHAR(50) CHARSET utf8)  READS SQL DATA
SELECT
dr.DimName,
mcup.LastName,
json_extract(gr.gravedata, "$.grave.Inventory.Items") AS Inventory,
gr.graveFullPath as GraveFile
FROM graves as gr 
INNER join mcuserprofiles as mcup on mcup.ID = gr.playerID 
inner join dimensionref as dr on dr.ID = gr.graveDim
where mcup.LastName = playerName or mcup.UUID = playerUUID$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `dimensionref`
--

DROP TABLE IF EXISTS `dimensionref`;
CREATE TABLE `dimensionref` (
  `ID` int(11) NOT NULL,
  `DimName` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `graves`
--

DROP TABLE IF EXISTS `graves`;
CREATE TABLE `graves` (
  `ID` int(11) NOT NULL,
  `playerID` int(11) NOT NULL,
  `graveDim` int(11) NOT NULL,
  `graveFullPath` text NOT NULL,
  `gravedata` json NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `itemref`
--

DROP TABLE IF EXISTS `itemref`;
CREATE TABLE `itemref` (
  `ID` int(11) NOT NULL,
  `ItemID` int(11) NOT NULL DEFAULT '0',
  `Name` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `mcprofiles`
--

DROP TABLE IF EXISTS `mcprofiles`;
CREATE TABLE `mcprofiles` (
  `ID` int(11) NOT NULL,
  `playerID` int(11) NOT NULL,
  `PlayerDat` json NOT NULL,
  `crc` char(64) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `mcstats`
--

DROP TABLE IF EXISTS `mcstats`;
CREATE TABLE `mcstats` (
  `ID` int(11) NOT NULL,
  `playerID` int(11) NOT NULL,
  `statsJson` json NOT NULL,
  `crc` char(64) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `mcuserprofiles`
--

DROP TABLE IF EXISTS `mcuserprofiles`;
CREATE TABLE `mcuserprofiles` (
  `ID` int(11) NOT NULL,
  `UUID` varchar(36) NOT NULL,
  `LastName` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Stellvertreter-Struktur des Views `show_latest_graves`
-- (Siehe unten für die tatsächliche Ansicht)
--
DROP VIEW IF EXISTS `show_latest_graves`;
CREATE TABLE `show_latest_graves` (
`DimName` varchar(50)
,`LastName` varchar(50)
,`Created` datetime(6)
,`posX` json
,`posY` json
,`posZ` json
,`GraveFile` text
);

-- --------------------------------------------------------

--
-- Stellvertreter-Struktur des Views `users_offlinedays_hoursplayed`
-- (Siehe unten für die tatsächliche Ansicht)
--
DROP VIEW IF EXISTS `users_offlinedays_hoursplayed`;
CREATE TABLE `users_offlinedays_hoursplayed` (
`UUID` varchar(36)
,`LastName` varchar(50)
,`offlineDays` bigint(21)
,`firstTimeJoined` datetime(6)
,`hoursPlayed` double(21,4)
);

-- --------------------------------------------------------

--
-- Struktur des Views `show_latest_graves`
--
DROP TABLE IF EXISTS `show_latest_graves`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `show_latest_graves`  AS  select `dr`.`DimName` AS `DimName`,`mcup`.`LastName` AS `LastName`,from_unixtime(substr(json_extract(`gr`.`gravedata`,'$.grave.Created'),1,(length(json_extract(`gr`.`gravedata`,'$.grave.Created')) - 3))) AS `Created`,json_extract(`gr`.`gravedata`,'$.grave.GraveLocation.X') AS `posX`,json_extract(`gr`.`gravedata`,'$.grave.GraveLocation.Y') AS `posY`,json_extract(`gr`.`gravedata`,'$.grave.GraveLocation.Z') AS `posZ`,`gr`.`graveFullPath` AS `GraveFile` from ((`graves` `gr` join `mcuserprofiles` `mcup` on((`mcup`.`ID` = `gr`.`playerID`))) join `dimensionref` `dr` on((`dr`.`ID` = `gr`.`graveDim`))) order by from_unixtime(substr(json_extract(`gr`.`gravedata`,'$.grave.Created'),1,(length(json_extract(`gr`.`gravedata`,'$.grave.Created')) - 3))) desc ;

-- --------------------------------------------------------

--
-- Struktur des Views `users_offlinedays_hoursplayed`
--
DROP TABLE IF EXISTS `users_offlinedays_hoursplayed`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `users_offlinedays_hoursplayed`  AS  select `mcup`.`UUID` AS `UUID`,`mcup`.`LastName` AS `LastName`,timestampdiff(DAY,now(),from_unixtime(substr(json_extract(`mcp`.`PlayerDat`,'$.grave.bukkit.lastPlayed'),1,(length(json_extract(`mcp`.`PlayerDat`,'$.grave.bukkit.lastPlayed')) - 3)))) AS `offlineDays`,from_unixtime(substr(json_extract(`mcp`.`PlayerDat`,'$.grave.bukkit.firstPlayed'),1,(length(json_extract(`mcp`.`PlayerDat`,'$.grave.bukkit.firstPlayed')) - 3))) AS `firstTimeJoined`,(json_extract(`mcs`.`statsJson`,'$.statplayOneMinute') / 72000) AS `hoursPlayed` from ((`mcprofiles` `mcp` join `mcstats` `mcs` on((`mcp`.`playerID` = `mcs`.`playerID`))) join `mcuserprofiles` `mcup` on((`mcup`.`ID` = `mcp`.`playerID`))) order by timestampdiff(DAY,now(),from_unixtime(substr(json_extract(`mcp`.`PlayerDat`,'$.grave.bukkit.lastPlayed'),1,(length(json_extract(`mcp`.`PlayerDat`,'$.grave.bukkit.lastPlayed')) - 3)))),(json_extract(`mcs`.`statsJson`,'$.statplayOneMinute') / 72000) desc ;

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `dimensionref`
--
ALTER TABLE `dimensionref`
  ADD PRIMARY KEY (`ID`);

--
-- Indizes für die Tabelle `graves`
--
ALTER TABLE `graves`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `FK_graves_mcuserprofiles` (`playerID`),
  ADD KEY `FK_graves_dimensionref` (`graveDim`);

--
-- Indizes für die Tabelle `itemref`
--
ALTER TABLE `itemref`
  ADD PRIMARY KEY (`ID`);

--
-- Indizes für die Tabelle `mcprofiles`
--
ALTER TABLE `mcprofiles`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `FK_mcjsondata_mcuserprofiles` (`playerID`);

--
-- Indizes für die Tabelle `mcstats`
--
ALTER TABLE `mcstats`
  ADD PRIMARY KEY (`ID`),
  ADD KEY `FK__mcuserprofiles` (`playerID`);

--
-- Indizes für die Tabelle `mcuserprofiles`
--
ALTER TABLE `mcuserprofiles`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `UUID` (`UUID`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `dimensionref`
--
ALTER TABLE `dimensionref`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;
--
-- AUTO_INCREMENT für Tabelle `graves`
--
ALTER TABLE `graves`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=184;
--
-- AUTO_INCREMENT für Tabelle `itemref`
--
ALTER TABLE `itemref`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT für Tabelle `mcprofiles`
--
ALTER TABLE `mcprofiles`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=383;
--
-- AUTO_INCREMENT für Tabelle `mcstats`
--
ALTER TABLE `mcstats`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=419;
--
-- AUTO_INCREMENT für Tabelle `mcuserprofiles`
--
ALTER TABLE `mcuserprofiles`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4010;
--
-- Constraints der exportierten Tabellen
--

--
-- Constraints der Tabelle `graves`
--
ALTER TABLE `graves`
  ADD CONSTRAINT `FK_graves_dimensionref` FOREIGN KEY (`graveDim`) REFERENCES `dimensionref` (`ID`),
  ADD CONSTRAINT `FK_graves_mcuserprofiles` FOREIGN KEY (`playerID`) REFERENCES `mcuserprofiles` (`ID`);

--
-- Constraints der Tabelle `mcprofiles`
--
ALTER TABLE `mcprofiles`
  ADD CONSTRAINT `FK_mcjsondata_mcuserprofiles` FOREIGN KEY (`playerID`) REFERENCES `mcuserprofiles` (`ID`);

--
-- Constraints der Tabelle `mcstats`
--
ALTER TABLE `mcstats`
  ADD CONSTRAINT `FK__mcuserprofiles` FOREIGN KEY (`playerID`) REFERENCES `mcuserprofiles` (`ID`);
