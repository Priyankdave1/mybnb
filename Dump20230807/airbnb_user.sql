-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: airbnb
-- ------------------------------------------------------
-- Server version	8.0.34

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
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (242355436,'123 Main St','Engineer','1990-01-15','John','Doe','john.doe','password123','1234567890123456'),(254345255,'789 Oak St','Accountant','1988-07-10','Michael','Johnson','michael.johnson','pass123','5678901234567890'),(254534643,'456 Elm St','Teacher','1995-03-20','Jane','Smith','jane.smith','mypassword','9876543210987654'),(346346343,'555 Walnut St','Artist','1991-12-08','Sophia','Lee','sophia.lee','1234567890','4567890123456789'),(346568346,'444 Birch St','Architect','1998-06-18','James','Miller','james.miller','testpw','7654321098765432'),(346646464,'222 Maple St','Lawyer','1992-09-05','William','Brown','william.brown','securepw','8765432109876543'),(563533452,'666 Cedar St','Chef','1989-02-28','Daniel','Wilson','daniel.wilson','pass1234','9876543210987654'),(646456643,'101 Pine St','Doctor','1985-11-25','Emily','Williams','emily.williams','qwerty','2345678901234567'),(768574346,'333 Cedar St','Writer','1982-04-30','Olivia','Jones','olivia.jones','password321','3456789012345678'),(875446664,'777 Oak St','Entrepreneur','1997-10-12','Isabella','Anderson','isabella.anderson','mypassword123','3456789012345678');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-08-07  3:30:05
