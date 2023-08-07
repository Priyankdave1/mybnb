USE airbnb;
SET FOREIGN_KEY_CHECKS = 0;
SET GROUP_CONCAT_MAX_LEN=32768;
SET @tables = NULL;
SELECT GROUP_CONCAT('`', table_name, '`') INTO @tables
  FROM information_schema.tables
  WHERE table_schema = (SELECT DATABASE());
SELECT IFNULL(@tables,'dummy') INTO @tables;
SET @tables = CONCAT('DROP TABLE IF EXISTS ', @tables);
PREPARE stmt FROM @tables;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
SET FOREIGN_KEY_CHECKS = 1;


CREATE TABLE `Listing` (
  `listingId` int NOT NULL AUTO_INCREMENT,
  `city` varchar(45) NOT NULL,
  `latitude` decimal(8,6) NOT NULL,
  `longitude` decimal(9,6) NOT NULL,
  `postalCode` varchar(45) NOT NULL,
  `country` varchar(45) NOT NULL,
  `type` varchar(45) NOT NULL,
  `address` varchar(45) NOT NULL,
  `bedrooms` int NOT NULL,
  `bathrooms` int NOT NULL,  
  PRIMARY KEY (`listingId`)
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


CREATE TABLE `Amenities` (
  `name` varchar(45) NOT NULL,
  `price` decimal(20,2) NOT NULL ,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Availability` (
  `dateAvailable` date NOT NULL,
  `price` decimal(20,2) NOT NULL,
  `listingId` int NOT NULL,
  `isAvailable` BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (`dateAvailable`,`listingId`),
  KEY `ListingFK_idx` (`listingId`),
  CONSTRAINT `ListingIdFK` FOREIGN KEY (`listingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `BookedBy` (
  `bookingId` int NOT NULL AUTO_INCREMENT,
  `listingId` int NOT NULL,
  `renterSIN` int NOT NULL,
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
  CONSTRAINT `RenterFK` FOREIGN KEY (`RenterSIN`) REFERENCES `User` (`SIN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `UserCreatesListing` (
  `hostSIN` int NOT NULL,
  `listingId` int NOT NULL,
  KEY `hostFK_idx` (`hostSIN`),
  KEY `listingFK_idx` (`listingId`),
  CONSTRAINT `FKtoListing` FOREIGN KEY (`listingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE,
  CONSTRAINT `hostFK` FOREIGN KEY (`hostSIN`) REFERENCES `User` (`SIN`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `ListingReviewAndComments` (
  `listingId` int NOT NULL,
  `renterSIN` int NOT NULL,
  `comment` longtext,
  `rating` int DEFAULT NULL,
  PRIMARY KEY (`listingId`,`renterSIN`),
  KEY `Renter_idx` (`renterSIN`),
  CONSTRAINT `Listing` FOREIGN KEY (`listingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE,
  CONSTRAINT `Renter` FOREIGN KEY (`renterSIN`) REFERENCES `User` (`SIN`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `ListingToAmenities` (
  `listingId` int NOT NULL,
  `amenity` varchar(45) NOT NULL,
  KEY `ListingFK_idx` (`ListingId`),
  KEY `AmenitiesFK` (`Amenity`),
  CONSTRAINT `AmenitiesFK` FOREIGN KEY (`Amenity`) REFERENCES `Amenities` (`name`) ON DELETE CASCADE,
  CONSTRAINT `ListingFK` FOREIGN KEY (`ListingId`) REFERENCES `Listing` (`listingId`) ON DELETE CASCADE
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


INSERT INTO User(SIN, address, occupation, dob, firstName, lastName, username, password) VALUES (111111111, 'Zesty Lane', 'Job', '1111-11-11', 'Yank', 'Moment', 'youjustgotpriyanked', 'password');


INSERT INTO Amenities (name, price) VALUES ('Hair dryer', 5.00);
INSERT INTO Amenities (name, price) VALUES ('Cleaning products', 3.50);
INSERT INTO Amenities (name, price) VALUES ('Shampoo', 4.00);
INSERT INTO Amenities (name, price) VALUES ('Conditioner', 4.00);
INSERT INTO Amenities (name, price) VALUES ('Body soap', 3.00);
INSERT INTO Amenities (name, price) VALUES ('Hot water', 0.00);
INSERT INTO Amenities (name, price) VALUES ('Shower gel', 4.50);
INSERT INTO Amenities (name, price) VALUES ('Essentials', 5.00);
INSERT INTO Amenities (name, price) VALUES ('Towels, bed sheets, soap, and toilet paper', 6.50);
INSERT INTO Amenities (name, price) VALUES ('Hangers', 2.50);
INSERT INTO Amenities (name, price) VALUES ('Bed linens', 5.50);
INSERT INTO Amenities (name, price) VALUES ('Extra pillows and blankets', 4.00);
INSERT INTO Amenities (name, price) VALUES ('Room-darkening shades', 2.50);
INSERT INTO Amenities (name, price) VALUES ('Iron', 3.50);
INSERT INTO Amenities (name, price) VALUES ('Smoke alarm', 1.00);
INSERT INTO Amenities (name, price) VALUES ('Carbon monoxide alarm', 0.50);
INSERT INTO Amenities (name, price) VALUES ('Fire extinguisher', 1.00);
INSERT INTO Amenities (name, price) VALUES ('Fast wifi', 4.00);
INSERT INTO Amenities (name, price) VALUES ('Refrigerator', 4.00);
INSERT INTO Amenities (name, price) VALUES ('Microwave', 3.00);
INSERT INTO Amenities (name, price) VALUES ('Cooking basics', 2.00);
INSERT INTO Amenities (name, price) VALUES ('Dishes and silverware', 2.00);
INSERT INTO Amenities (name, price) VALUES ('Freezer', 3.00);
INSERT INTO Amenities (name, price) VALUES ('Oven', 4.00);
INSERT INTO Amenities (name, price) VALUES ('Hot water kettle', 1.00);
INSERT INTO Amenities (name, price) VALUES ('Coffee maker', 1.00);
INSERT INTO Amenities (name, price) VALUES ('Wine glasses', 1.00);
INSERT INTO Amenities (name, price) VALUES ('Toaster', 2.00);
INSERT INTO Amenities (name, price) VALUES ('Barbecue utensils', 1.00);
INSERT INTO Amenities (name, price) VALUES ('Grill, charcoal, bamboo skewers/iron skewers, etc.', 2.00);
INSERT INTO Amenities (name, price) VALUES ('Dining table', 6.00);
INSERT INTO Amenities (name, price) VALUES ('Private entrance', 5.00);
INSERT INTO Amenities (name, price) VALUES ('Free parking on premises', 5.00);
INSERT INTO Amenities (name, price) VALUES ('Free street parking', 3.00);

