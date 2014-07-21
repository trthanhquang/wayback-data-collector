-- phpMyAdmin SQL Dump
-- version 4.1.14
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Jul 21, 2014 at 07:29 PM
-- Server version: 5.6.17
-- PHP Version: 5.5.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `crawling`
--
CREATE DATABASE IF NOT EXISTS `crawling` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `crawling`;

-- --------------------------------------------------------

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
CREATE TABLE IF NOT EXISTS `item` (
  `itemID` int(4) NOT NULL,
  `softwareID` int(6) DEFAULT NULL,
  `app_name` char(128) NOT NULL,
  `total_down` int(8) DEFAULT NULL,
  `sub_cat_name` char(128) DEFAULT NULL,
  `Website` char(255) DEFAULT NULL,
  `Feature_URL` text,
  `Price_URL` text,
  `Comments` text,
  PRIMARY KEY (`itemID`,`app_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `report`
--

DROP TABLE IF EXISTS `report`;
CREATE TABLE IF NOT EXISTS `report` (
  `itemID` int(4) NOT NULL,
  `itemName` char(128) NOT NULL,
  `snapshot_date` date NOT NULL,
  `price` longtext NOT NULL,
  `feature` longtext NOT NULL,
  PRIMARY KEY (`itemID`,`itemName`,`snapshot_date`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `snapshot_feature`
--

DROP TABLE IF EXISTS `snapshot_feature`;
CREATE TABLE IF NOT EXISTS `snapshot_feature` (
  `itemID` int(4) NOT NULL,
  `url_list_index` int(5) NOT NULL,
  `snapshot_date` date NOT NULL,
  `snapshot_url` text NOT NULL,
  `crawl_data` longtext NOT NULL,
  PRIMARY KEY (`itemID`,`url_list_index`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4
/*!50100 PARTITION BY RANGE (itemID)
(PARTITION p0 VALUES LESS THAN (228) ENGINE = MyISAM,
 PARTITION p1 VALUES LESS THAN (456) ENGINE = MyISAM,
 PARTITION p3 VALUES LESS THAN (683) ENGINE = MyISAM,
 PARTITION p4 VALUES LESS THAN (910) ENGINE = MyISAM,
 PARTITION p5 VALUES LESS THAN (1138) ENGINE = MyISAM) */;

-- --------------------------------------------------------

--
-- Table structure for table `snapshot_price`
--

DROP TABLE IF EXISTS `snapshot_price`;
CREATE TABLE IF NOT EXISTS `snapshot_price` (
  `itemID` int(4) NOT NULL,
  `url_list_index` int(5) NOT NULL,
  `snapshot_date` date NOT NULL,
  `snapshot_url` text NOT NULL,
  `crawl_data` longtext NOT NULL,
  PRIMARY KEY (`itemID`,`url_list_index`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4
/*!50100 PARTITION BY RANGE (itemID)
(PARTITION p0 VALUES LESS THAN (228) ENGINE = MyISAM,
 PARTITION p1 VALUES LESS THAN (456) ENGINE = MyISAM,
 PARTITION p3 VALUES LESS THAN (683) ENGINE = MyISAM,
 PARTITION p4 VALUES LESS THAN (910) ENGINE = MyISAM,
 PARTITION p5 VALUES LESS THAN (1138) ENGINE = MyISAM) */;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;