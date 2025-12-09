-- MySQL dump 10.13  Distrib 5.7.44, for Linux (x86_64)
--
-- Host: localhost    Database: prestashop
-- ------------------------------------------------------
-- Server version	5.7.44

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
-- Table structure for table `ps_module`
--

DROP TABLE IF EXISTS `ps_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_module` (
  `id_module` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `version` varchar(8) NOT NULL,
  PRIMARY KEY (`id_module`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_module`
--

LOCK TABLES `ps_module` WRITE;
/*!40000 ALTER TABLE `ps_module` DISABLE KEYS */;
INSERT INTO `ps_module` VALUES (1,'blockwishlist',1,'2.1.2'),(2,'contactform',1,'4.4.1'),(3,'dashactivity',1,'2.1.0'),(4,'dashtrends',1,'2.1.2'),(5,'dashgoals',1,'2.0.4'),(6,'dashproducts',1,'2.1.3'),(7,'graphnvd3',1,'2.0.3'),(8,'gridhtml',1,'2.0.3'),(9,'gsitemap',1,'4.3.0'),(10,'pagesnotfound',1,'2.0.2'),(11,'productcomments',1,'5.0.3'),(12,'ps_banner',1,'2.1.2'),(13,'ps_categorytree',1,'2.0.3'),(14,'ps_checkpayment',1,'2.0.6'),(15,'ps_contactinfo',1,'3.3.2'),(16,'ps_crossselling',1,'2.0.2'),(17,'ps_currencyselector',1,'2.1.1'),(18,'ps_customeraccountlinks',1,'3.2.0'),(19,'ps_customersignin',1,'2.0.5'),(20,'ps_customtext',1,'4.2.1'),(21,'ps_dataprivacy',1,'2.1.1'),(22,'ps_emailsubscription',1,'2.7.1'),(24,'ps_faviconnotificationbo',1,'2.1.3'),(25,'ps_featuredproducts',1,'2.1.4'),(26,'ps_imageslider',1,'3.1.3'),(27,'ps_languageselector',1,'2.1.3'),(28,'ps_linklist',1,'5.0.5'),(29,'ps_mainmenu',1,'2.3.2'),(30,'ps_searchbar',1,'2.1.3'),(31,'ps_sharebuttons',1,'2.1.2'),(32,'ps_shoppingcart',1,'2.0.7'),(33,'ps_socialfollow',1,'2.3.0'),(34,'ps_themecusto',1,'1.2.3'),(35,'ps_wirepayment',1,'2.1.3'),(36,'statsbestcategories',1,'2.0.1'),(37,'statsbestcustomers',1,'2.0.4'),(38,'statsbestproducts',1,'2.0.1'),(39,'statsbestsuppliers',1,'2.0.2'),(40,'statsbestvouchers',1,'2.0.1'),(41,'statscarrier',1,'2.0.1'),(42,'statscatalog',1,'2.0.3'),(43,'statscheckup',1,'2.0.2'),(44,'statsdata',1,'2.1.1'),(45,'statsforecast',1,'2.0.4'),(46,'statsnewsletter',1,'2.0.3'),(47,'statspersonalinfos',1,'2.0.4'),(48,'statsproduct',1,'2.1.1'),(49,'statsregistrations',1,'2.0.1'),(50,'statssales',1,'2.1.0'),(51,'statssearch',1,'2.0.2'),(52,'statsstock',1,'2.0.1'),(53,'welcome',1,'6.0.9'),(54,'psgdpr',1,'1.4.3'),(55,'ps_mbo',1,'3.3.1'),(56,'ps_buybuttonlite',1,'1.0.1'),(57,'ps_checkout',1,'7.5.0.6'),(58,'ps_facebook',1,'1.38.16'),(59,'blockreassurance',1,'5.1.2'),(60,'ps_facetedsearch',1,'3.12.1');
/*!40000 ALTER TABLE `ps_module` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-09 19:36:14
