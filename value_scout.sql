-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: value_scout
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `current_price` decimal(10,2) DEFAULT NULL,
  `target_price` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` tinyint(1) DEFAULT '0',
  `asin` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,1,'Man Cotton Blend Graphic Print Round Neck Half Sleeve Drop Shoulder Oversized T Shirt (Color Navy Blue)',299.00,500.00,'2025-11-13 16:19:21',1,'B0FHDKBLXX'),(2,1,'Hoodie for Boys | Black Navy Maroon Colour Hoodies | New Trending Anime Tshirts | Itachi Uchiha Printed Hooded Sweatshirt for Boy',464.00,500.00,'2025-11-13 16:19:24',1,'B0DRVCTR8R'),(3,1,'Jin Woo X Shadow Monarch Solo Leveling Printed Anime Oversized T-Shirt - Multi Color',459.00,500.00,'2025-11-14 14:59:33',1,'B0DYJ8S8B7');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'samarpan','samarpandahal39@gmail.com','scrypt:32768:8:1$SPvZeF5NcjQD8vtq$a5fb8e14ade871ed5becd67f49f998919730956b5561efc2ea99b995bf4e65b20a826490c080623611c3668584afd9496dd9162663aed89d5ccd1034ffc69405','2025-10-16 17:58:56'),(5,'sam','samarpandahal20@gmail.com','scrypt:32768:8:1$890eyNyiO3kJ0rzx$d8501d555dfdcce96b61b8ba37cea9152d4b04c77bc9ff88ba064d01cf23411d2b6dc20ee69324610835a805579a9afb35c7cc98e628d38518bbfbd2c0a9f3de','2025-10-24 13:54:48');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist`
--

DROP TABLE IF EXISTS `wishlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `link` text,
  `price` varchar(50) DEFAULT NULL,
  `thumbnail` text,
  `rating` varchar(20) DEFAULT NULL,
  `reviews` varchar(50) DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  `asin` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist`
--

LOCK TABLES `wishlist` WRITE;
/*!40000 ALTER TABLE `wishlist` DISABLE KEYS */;
INSERT INTO `wishlist` VALUES (45,1,'Jin Woo X Shadow Monarch Solo Leveling Printed Anime Oversized T-Shirt - Multi Color','https://www.amazon.in/crazymonk-Monarch-Leveling-Printed-Oversized/dp/B0DYJ8S8B7/ref=sr_1_14?dib=eyJ2IjoiMSJ9.BDSLFwsVVMFHgGg_GpXe4w_MlvafHqCdUZ5APZxcqLg8Ekx92zc3XPv-IjGCoDkH9gfpX0JVNg_5jGbYzZiy-DDvh1m-V9AXQQIArZ1BxstGFkR5aK5pYD-XRYBVC6bbX25-T_iMgeHCpNaqU47rp8iVonmWBEg_xVPG_l-Td5T8jQH5Hx1lHWzzEi7yl_hR9f8E8cofOT9hEMH3QooTMjdg123TJ9SfEhUAiahqDShAT9n39yACH-oebrXw74vSftDmAPL1lUZZNfSL8K-DLyRdUSGRui9T9q5MtsO5f64.95H1ydnehsIYcGnxA1qNQhWazy4hpucpJdFU6t5hT8E&dib_tag=se&keywords=anime+tshirts&qid=1763131594&sr=8-14','₹459','https://m.media-amazon.com/images/I/6126t1SJn1L._AC_UL320_.jpg','4.7','35','Amazon','B0DYJ8S8B7'),(50,1,'Bucklemen Boys Printed Oversized T Shirt','https://www.google.co.in/search?ibp=oshop&q=anime tshirt in flipkart&prds=catalogid:16243689524252515522,headlineOfferDocid:14871899113954898379,imageDocid:3812786254423973041,gpcid:13804189796642122139,mid:576462848352931520,pvt:a&hl=en&gl=in&udm=28','₹279','https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcSPF0Y6-S6nOvqzbjL7qE12cvjlqqJ-4qkJvEv1SBUGCXlmrc6tD_kWkcGUhwc','N/A','N/A','Flipkart',NULL);
/*!40000 ALTER TABLE `wishlist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist_tracking`
--

DROP TABLE IF EXISTS `wishlist_tracking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlist_tracking` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `target_price` float NOT NULL,
  `asin` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `wishlist_tracking_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist_tracking`
--

LOCK TABLES `wishlist_tracking` WRITE;
/*!40000 ALTER TABLE `wishlist_tracking` DISABLE KEYS */;
/*!40000 ALTER TABLE `wishlist_tracking` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-18 21:45:26
