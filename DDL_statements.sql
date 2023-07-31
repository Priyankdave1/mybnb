CREATE TABLE `Amenities` (
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Availability` (
  `dateAvailable` date NOT NULL,
  `price` decimal(20,2) NOT NULL,
  `listingId` int NOT NULL,
  PRIMARY KEY (`dateAvailable`,`listingId`),
  KEY `ListingFK_idx` (`listingId`),
  CONSTRAINT `ListingIdFK` FOREIGN KEY (`listingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `BookedBy` (
  `BookingId` int NOT NULL AUTO_INCREMENT,
  `ListingId` int NOT NULL,
  `RenterSIN` int NOT NULL,
  `startDate` date DEFAULT NULL,
  `endDate` date DEFAULT NULL,
  `isCancelled` tinyint NOT NULL DEFAULT '0',
  `cancelledBy` int DEFAULT NULL,
  PRIMARY KEY (`BookingId`),
  KEY `FKlistingID_idx` (`ListingId`),
  KEY `RenterFK_idx` (`RenterSIN`),
  KEY `cancelledByFK_idx` (`cancelledBy`),
  CONSTRAINT `cancelledByFK` FOREIGN KEY (`cancelledBy`) REFERENCES `User` (`SIN`),
  CONSTRAINT `FKlistingID` FOREIGN KEY (`ListingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE,
  CONSTRAINT `RenterFK` FOREIGN KEY (`RenterSIN`) REFERENCES `Renter` (`SIN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Host` (
  `SIN` int NOT NULL,
  KEY `SIN_idx` (`SIN`),
  CONSTRAINT `FK_Host_User` FOREIGN KEY (`SIN`) REFERENCES `User` (`SIN`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `HostCreatesListing` (
  `hostSIN` int NOT NULL,
  `listingId` int NOT NULL,
  KEY `hostFK_idx` (`hostSIN`),
  KEY `listingFK_idx` (`listingId`),
  CONSTRAINT `FKtoListing` FOREIGN KEY (`listingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE,
  CONSTRAINT `hostFK` FOREIGN KEY (`hostSIN`) REFERENCES `Host` (`SIN`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Listing` (
  `listingId` int NOT NULL AUTO_INCREMENT,
  `city` varchar(45) NOT NULL,
  `latitude` decimal(8,6) NOT NULL,
  `longitude` decimal(9,6) NOT NULL,
  `postalCode` varchar(45) NOT NULL,
  `country` varchar(45) NOT NULL,
  `type` varchar(45) NOT NULL,
  `address` varchar(45) NOT NULL,
  PRIMARY KEY (`listingId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `ListingReviewAndComments` (
  `listingId` int NOT NULL,
  `renterSIN` int NOT NULL,
  `comment` longtext,
  `rating` int DEFAULT NULL,
  PRIMARY KEY (`listingId`,`renterSIN`),
  KEY `Renter_idx` (`renterSIN`),
  CONSTRAINT `Listing` FOREIGN KEY (`listingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE,
  CONSTRAINT `Renter` FOREIGN KEY (`renterSIN`) REFERENCES `Renter` (`SIN`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `ListingToAmenities` (
  `ListingId` int NOT NULL,
  `Amenity` varchar(45) NOT NULL,
  KEY `ListingFK_idx` (`ListingId`),
  KEY `AmenitiesFK` (`Amenity`),
  CONSTRAINT `AmenitiesFK` FOREIGN KEY (`Amenity`) REFERENCES `Amenities` (`name`) ON DELETE CASCADE,
  CONSTRAINT `ListingFK` FOREIGN KEY (`ListingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Renter` (
  `SIN` int NOT NULL,
  KEY `SIN_idx` (`SIN`),
  CONSTRAINT `SIN` FOREIGN KEY (`SIN`) REFERENCES `User` (`SIN`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `User` (
  `SIN` int NOT NULL,
  `address` varchar(45) NOT NULL,
  `occupation` varchar(45) NOT NULL,
  `dob` date NOT NULL,
  `firstName` varchar(45) NOT NULL,
  `lastName` varchar(45) NOT NULL,
  `username` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  PRIMARY KEY (`SIN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `UserReviews` (
  `commentedOn` int NOT NULL,
  `commentedBy` int DEFAULT NULL,
  `comment` longtext,
  `rating` int DEFAULT NULL,
  PRIMARY KEY (`commentedOn`),
  KEY `CommentedBy_idx` (`commentedBy`),
  CONSTRAINT `CommentedBy` FOREIGN KEY (`commentedBy`) REFERENCES `User` (`SIN`) ON DELETE CASCADE,
  CONSTRAINT `CommentedOn` FOREIGN KEY (`commentedOn`) REFERENCES `User` (`SIN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
