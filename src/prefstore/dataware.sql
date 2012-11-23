-- MySQL dump 10.13  Distrib 5.1.63, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: dataware
-- ------------------------------------------------------
-- Server version	5.1.63-0ubuntu0.11.10.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tblDatawareCatalogs`
--

DROP TABLE IF EXISTS `tblDatawareCatalogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblDatawareCatalogs` (
  `catalog_uri` varchar(256) NOT NULL,
  `resource_id` varchar(256) NOT NULL,
  `registered` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`catalog_uri`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblDatawareCatalogs`
--

LOCK TABLES `tblDatawareCatalogs` WRITE;
/*!40000 ALTER TABLE `tblDatawareCatalogs` DISABLE KEYS */;
INSERT INTO `tblDatawareCatalogs` VALUES ('http://datawarecatalog.appspot.com','Q/1l85fnHL65rt3mUoqQx2nEq2ssT1EM6rA4RwkKJRw=',1350638949);
/*!40000 ALTER TABLE `tblDatawareCatalogs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblDatawareExecutions`
--

DROP TABLE IF EXISTS `tblDatawareExecutions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblDatawareExecutions` (
  `execution_id` int(11) NOT NULL AUTO_INCREMENT,
  `processor_id` varchar(256) NOT NULL,
  `parameters` varchar(256) NOT NULL,
  `result` text,
  `executed` int(11) unsigned NOT NULL,
  PRIMARY KEY (`execution_id`),
  KEY `processor_id` (`processor_id`),
  CONSTRAINT `tblDatawareExecutions_ibfk_1` FOREIGN KEY (`processor_id`) REFERENCES `tblDatawareProcessors` (`access_token`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblDatawareExecutions`
--

LOCK TABLES `tblDatawareExecutions` WRITE;
/*!40000 ALTER TABLE `tblDatawareExecutions` DISABLE KEYS */;
/*!40000 ALTER TABLE `tblDatawareExecutions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblDatawareInstalls`
--

DROP TABLE IF EXISTS `tblDatawareInstalls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblDatawareInstalls` (
  `user_id` varchar(256) NOT NULL,
  `catalog_uri` varchar(256) NOT NULL,
  `install_token` varchar(256) DEFAULT NULL,
  `state` varchar(256) NOT NULL,
  `registered` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `catalog_uri` (`catalog_uri`),
  CONSTRAINT `tblDatawareInstalls_ibfk_1` FOREIGN KEY (`catalog_uri`) REFERENCES `tblDatawareCatalogs` (`catalog_uri`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblDatawareInstalls`
--

LOCK TABLES `tblDatawareInstalls` WRITE;
/*!40000 ALTER TABLE `tblDatawareInstalls` DISABLE KEYS */;
INSERT INTO `tblDatawareInstalls` VALUES ('https://www.google.com/accounts/o8/id?id=AItOawkDmzFL9cXjvd-48U8L_eb-Wbf7dB-c-P4','http://datawarecatalog.appspot.com','EZ6*n84PjhzOMA3hFOV/8IWGSh6ApI26nPc7WUy2ZjM=','bkpGNMlzwgEXyrdbR1PqVqOaWYJZ8bQTArhdNdZXi7A=',1350639003);
/*!40000 ALTER TABLE `tblDatawareInstalls` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblDatawareProcessors`
--

DROP TABLE IF EXISTS `tblDatawareProcessors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblDatawareProcessors` (
  `access_token` varchar(256) NOT NULL,
  `client_id` varchar(256) NOT NULL,
  `user_id` varchar(256) NOT NULL,
  `expiry_time` int(11) unsigned NOT NULL,
  `query` text NOT NULL,
  `checksum` varchar(256) NOT NULL,
  PRIMARY KEY (`access_token`),
  UNIQUE KEY `client_id` (`client_id`,`user_id`,`checksum`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblDatawareProcessors`
--

LOCK TABLES `tblDatawareProcessors` WRITE;
/*!40000 ALTER TABLE `tblDatawareProcessors` DISABLE KEYS */;
/*!40000 ALTER TABLE `tblDatawareProcessors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblUserDetails`
--

DROP TABLE IF EXISTS `tblUserDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblUserDetails` (
  `user_id` varchar(256) NOT NULL,
  `user_name` varchar(64) DEFAULT NULL,
  `email` varchar(256) DEFAULT NULL,
  `registered` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `UNIQUE` (`user_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblUserDetails`
--

LOCK TABLES `tblUserDetails` WRITE;
/*!40000 ALTER TABLE `tblUserDetails` DISABLE KEYS */;
INSERT INTO `tblUserDetails` VALUES ('https://www.google.com/accounts/o8/id?id=AItOawkDmzFL9cXjvd-48U8L_eb-Wbf7dB-c-P4','tlodgeresource','tlodge@gmail.com',1350638532);
/*!40000 ALTER TABLE `tblUserDetails` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-11-16  9:52:47
