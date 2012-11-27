-- MySQL dump 10.13  Distrib 5.1.63, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: homework
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
-- Table structure for table `urls`
--

DROP TABLE IF EXISTS `urls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `urls` (
  `ts` varchar(20) NOT NULL DEFAULT '',
  `macaddr` varchar(19) NOT NULL DEFAULT '',
  `ipaddr` varchar(16) DEFAULT NULL,
  `url` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`ts`,`macaddr`,`url`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `urls`
--

LOCK TABLES `urls` WRITE;
/*!40000 ALTER TABLE `urls` DISABLE KEYS */;
INSERT INTO `urls` VALUES ('2012/09/21:13:30:17','60:c5:47:8c:f9:0a','192.168.1.101','1-courier.push.apple.com'),('2012/09/21:13:30:17','60:c5:47:8c:f9:0a','192.168.1.101','www.apple.com'),('2012/09/21:13:30:17','60:c5:47:8c:f9:0a','192.168.1.101','15-courier.push.apple.com'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','wwwcache.cs.nott.ac.uk'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','db._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','b._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','dr._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','lb._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','r._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','b._dns-sd._udp.localdomain'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','db._dns-sd._udp.localdomain'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','r._dns-sd._udp.localdomain'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','lb._dns-sd._udp.localdomain'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','dr._dns-sd._udp.localdomain'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','www.google.com'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','dsn13.d.skype.net'),('2012/09/21:13:30:18','60:c5:47:8c:f9:0a','192.168.1.101','conn.skype.com'),('2012/09/21:13:30:20','60:c5:47:8c:f9:0a','192.168.1.101','101.1.168.192.in-addr.arpa'),('2012/09/21:13:30:21','60:c5:47:8c:f9:0a','192.168.1.101','www.apple.com'),('2012/09/21:13:30:36','60:c5:47:8c:f9:0a','192.168.1.101','mail.google.com'),('2012/09/21:13:30:39','60:c5:47:8c:f9:0a','192.168.1.101','e3191.c.akamaiedge.net'),('2012/09/21:13:31:01','60:c5:47:8c:f9:0a','192.168.1.101','e3191.c.akamaiedge.net'),('2012/09/21:13:31:14','60:c5:47:8c:f9:0a','192.168.1.101','news.ycombinator.com'),('2012/09/21:13:31:23','60:c5:47:8c:f9:0a','192.168.1.101','e3191.c.akamaiedge.net'),('2012/09/21:13:31:45','60:c5:47:8c:f9:0a','192.168.1.101','e3191.c.akamaiedge.net'),('2012/09/21:13:32:08','60:c5:47:8c:f9:0a','192.168.1.101','e3191.c.akamaiedge.net'),('2012/09/21:13:32:30','60:c5:47:8c:f9:0a','192.168.1.101','e3191.c.akamaiedge.net'),('2012/09/21:13:33:36','60:c5:47:8c:f9:0a','192.168.1.101','MYWIFIPLUG.localdomain'),('2012/09/21:13:34:07','60:c5:47:8c:f9:0a','192.168.1.101','wwwcache.cs.nott.ac.uk'),('2012/09/21:13:34:12','60:c5:47:8c:f9:0a','192.168.1.101','mail.google.com'),('2012/09/21:13:34:34','60:c5:47:8c:f9:0a','192.168.1.101','marian.cs.nott.ac.uk'),('2012/09/21:13:34:45','60:c5:47:8c:f9:0a','192.168.1.101','safebrowsing.google.com'),('2012/09/21:13:34:45','60:c5:47:8c:f9:0a','192.168.1.101','safebrowsing-cache.google.com'),('2012/09/21:13:37:33','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:13:45:26','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:13:48:18','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:13:57:23','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:13:58:56','60:c5:47:8c:f9:0a','192.168.1.101','p01-keyvalueservice.icloud.com'),('2012/09/21:13:58:59','60:c5:47:8c:f9:0a','192.168.1.101','keyvalueservice.icloud.com'),('2012/09/21:14:03:13','60:c5:47:8c:f9:0a','192.168.1.101','sb.l.google.com'),('2012/09/21:14:03:13','60:c5:47:8c:f9:0a','192.168.1.101','safebrowsing.cache.l.google.com'),('2012/09/21:14:04:40','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:12:33','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:16:15','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:20:08','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:27:33','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:30:18','60:c5:47:8c:f9:0a','192.168.1.101','b._dns-sd._udp.localdomain'),('2012/09/21:14:30:18','60:c5:47:8c:f9:0a','192.168.1.101','db._dns-sd._udp.localdomain'),('2012/09/21:14:30:18','60:c5:47:8c:f9:0a','192.168.1.101','r._dns-sd._udp.localdomain'),('2012/09/21:14:30:18','60:c5:47:8c:f9:0a','192.168.1.101','lb._dns-sd._udp.localdomain'),('2012/09/21:14:30:18','60:c5:47:8c:f9:0a','192.168.1.101','dr._dns-sd._udp.localdomain'),('2012/09/21:14:30:24','60:c5:47:8c:f9:0a','192.168.1.101','dr._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:14:30:24','60:c5:47:8c:f9:0a','192.168.1.101','lb._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:14:30:24','60:c5:47:8c:f9:0a','192.168.1.101','db._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:14:30:24','60:c5:47:8c:f9:0a','192.168.1.101','b._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:14:30:24','60:c5:47:8c:f9:0a','192.168.1.101','r._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:14:32:20','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:33:30','60:c5:47:8c:f9:0a','192.168.1.101','sb.l.google.com'),('2012/09/21:14:33:30','60:c5:47:8c:f9:0a','192.168.1.101','safebrowsing.cache.l.google.com'),('2012/09/21:14:36:00','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:39:57','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:47:11','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:50:36','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:14:57:33','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:15:02:33','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:15:04:37','60:c5:47:8c:f9:0a','192.168.1.101','sb.l.google.com'),('2012/09/21:15:04:37','60:c5:47:8c:f9:0a','192.168.1.101','safebrowsing.cache.l.google.com'),('2012/09/21:15:06:32','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:15:10:09','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:15:17:33','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:15:21:01','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:15:28:24','60:c5:47:8c:f9:0a','192.168.1.101','googlemail.l.google.com'),('2012/09/21:15:29:43','60:c5:47:8c:f9:0a','192.168.1.101','b._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:15:29:43','60:c5:47:8c:f9:0a','192.168.1.101','dr._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:15:29:43','60:c5:47:8c:f9:0a','192.168.1.101','lb._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:15:29:43','60:c5:47:8c:f9:0a','192.168.1.101','b._dns-sd._udp.localdomain'),('2012/09/21:15:29:43','60:c5:47:8c:f9:0a','192.168.1.101','r._dns-sd._udp.localdomain'),('2012/09/21:15:29:56','60:c5:47:8c:f9:0a','192.168.1.101','lb._dns-sd._udp.localdomain'),('2012/09/21:15:30:18','60:c5:47:8c:f9:0a','192.168.1.101','db._dns-sd._udp.localdomain'),('2012/09/21:15:30:18','60:c5:47:8c:f9:0a','192.168.1.101','dr._dns-sd._udp.localdomain'),('2012/09/21:15:30:23','60:c5:47:8c:f9:0a','192.168.1.101','db._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:15:30:23','60:c5:47:8c:f9:0a','192.168.1.101','r._dns-sd._udp.0.1.168.192.in-addr.arpa'),('2012/09/21:15:32:33','60:c5:47:8c:f9:0a','192.168.1.101','mail.google.com'),('2012/09/21:15:32:57','60:c5:47:8c:f9:0a','192.168.1.101','safebrowsing.google.com'),('2012/09/21:15:32:57','60:c5:47:8c:f9:0a','192.168.1.101','safebrowsing-cache.google.com');
/*!40000 ALTER TABLE `urls` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `energy`
--

DROP TABLE IF EXISTS `energy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `energy` (
  `ts` varchar(20) NOT NULL,
  `sensorid` int(11) NOT NULL DEFAULT '0',
  `watts` float DEFAULT NULL,
  PRIMARY KEY (`ts`,`sensorid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `energy`
--

LOCK TABLES `energy` WRITE;
/*!40000 ALTER TABLE `energy` DISABLE KEYS */;
/*!40000 ALTER TABLE `energy` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-11-16  9:42:50
