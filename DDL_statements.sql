use airbnb;
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

-- SET FOREIGN_KEY_CHECKS = 0;
-- DROP TABLE IF EXISTS `listing`;
-- DROP TABLE IF EXISTS `user`;
-- DROP TABLE IF EXISTS `amenities`;
-- DROP TABLE IF EXISTS `bookedBy`;
-- DROP TABLE IF EXISTS `availability`;
-- DROP TABLE IF EXISTS `userCreatesListing`;
-- DROP TABLE IF EXISTS `listingToAmenities`;
-- DROP TABLE IF EXISTS `userReviews`;
-- DROP TABLE IF EXISTS `listingReviewAndComments`;
-- SET FOREIGN_KEY_CHECKS = 1;




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
  `creditCardNO` varchar(45) NOT NULL,
  PRIMARY KEY (`SIN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `Amenities` (
  `name` varchar(75) NOT NULL,
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
  `amenity` varchar(75) NOT NULL,
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

-- Insert statements for User table
INSERT INTO User (SIN, address, occupation, dob, firstName, lastName, username, password, creditCardNO)
VALUES
  (242355436, '123 Main St', 'Engineer', '1990-01-15', 'John', 'Doe', 'john.doe', 'password123', '1234567890123456'),
  (254534643, '456 Elm St', 'Teacher', '1995-03-20', 'Jane', 'Smith', 'jane.smith', 'mypassword', '9876543210987654'),
  (254345255, '789 Oak St', 'Accountant', '1988-07-10', 'Michael', 'Johnson', 'michael.johnson', 'pass123', '5678901234567890'),
  (646456643, '101 Pine St', 'Doctor', '1985-11-25', 'Emily', 'Williams', 'emily.williams', 'qwerty', '2345678901234567'),
  (346646464, '222 Maple St', 'Lawyer', '1992-09-05', 'William', 'Brown', 'william.brown', 'securepw', '8765432109876543'),
  (768574346, '333 Cedar St', 'Writer', '1982-04-30', 'Olivia', 'Jones', 'olivia.jones', 'password321', '3456789012345678'),
  (346568346, '444 Birch St', 'Architect', '1998-06-18', 'James', 'Miller', 'james.miller', 'testpw', '7654321098765432'),
  (346346343, '555 Walnut St', 'Artist', '1991-12-08', 'Sophia', 'Lee', 'sophia.lee', '1234567890', '4567890123456789'),
  (563533452, '666 Cedar St', 'Chef', '1989-02-28', 'Daniel', 'Wilson', 'daniel.wilson', 'pass1234', '9876543210987654'),
  (875446664, '777 Oak St', 'Entrepreneur', '1997-10-12', 'Isabella', 'Anderson', 'isabella.anderson', 'mypassword123', '3456789012345678');

-- Insert statements for Listing table
INSERT INTO Listing (city, latitude, longitude, postalCode, country, type, address, bedrooms, bathrooms)
VALUES
  ('New York', 40.7128, -74.0060, '10001', 'USA', 'Apartment', '123 Main St, Apt 1', 2, 1),
  ('Los Angeles', 34.0522, -118.2437, '90001', 'USA', 'House', '456 Elm St', 3, 2),
  ('Chicago', 41.8781, -87.6298, '60601', 'USA', 'Apartment', '789 Oak St, Apt 5', 1, 1),
  ('San Francisco', 37.7749, -122.4194, '94101', 'USA', 'House', '101 Pine St', 4, 3),
  ('Miami', 25.7617, -80.1918, '33101', 'USA', 'Room', '222 Maple St, Room 3', 1, 1),
  ('Leduc',45.000000,32.000000,'T0C0V0','Canada','house','121 Sparrow Street',3,3);


INSERT INTO UserCreatesListing (hostSIN, listingId)
VALUES
  (242355436, 1),
  (254534643, 2),
  (254345255, 3),
  (646456643, 4),
  (346646464, 5),
  (563533452, 6);


INSERT INTO Availability (dateAvailable, price, listingId)
VALUES
  ('2023-08-01', 100.00, 1),
  ('2023-08-02', 100.00, 1),
  ('2023-08-03', 100.00, 1),
  ('2023-08-04', 100.00, 1),
  ('2023-08-05', 100.00, 1),
  ('2023-08-06', 100.00, 1),
  ('2023-08-07', 100.00, 1),
  ('2023-08-08', 100.00, 1),
  ('2023-08-09', 100.00, 1),
  ('2023-08-10', 100.00, 1),
  ('2024-08-11', 150.00, 1),
  ('2024-08-12', 150.00, 1),
  ('2024-08-13', 150.00, 1),
  ('2024-08-14', 150.00, 1),
  ('2024-08-15', 150.00, 1),
  ('2024-08-16', 150.00, 1),
  ('2023-12-17', 150.00, 2),
  ('2023-12-18', 150.00, 2),
  ('2023-12-19', 150.00, 2),
  ('2023-12-20', 150.00, 2),
  ('2023-11-21', 80.00, 3),
  ('2023-11-22', 80.00, 3),
  ('2023-11-23', 80.00, 3),
  ('2023-11-24', 80.00, 3),
  ('2023-11-25', 80.00, 3),
  ('2023-11-26', 80.00, 3),
  ('2023-11-27', 80.00, 3),
  ('2023-11-28', 80.00, 3),
  ('2023-11-29', 80.00, 3),
  ('2023-11-30', 80.00, 3),
  ('2023-10-31', 200.00, 4),
  ('2023-11-01', 200.00, 4),
  ('2023-11-02', 200.00, 4),
  ('2023-11-03', 200.00, 4),
  ('2023-11-04', 200.00, 4),
  ('2023-11-05', 200.00, 4),
  ('2023-11-06', 200.00, 4),
  ('2023-11-07', 200.00, 4),
  ('2023-11-08', 200.00, 4),
  ('2023-11-09', 200.00, 4),
  ('2023-09-10', 50.00, 5),
  ('2023-09-11', 50.00, 5),
  ('2023-09-12', 50.00, 5),
  ('2023-09-13', 50.00, 5),
  ('2023-09-14', 50.00, 5),
  ('2023-09-15', 50.00, 5),
  ('2023-09-16', 50.00, 5),
  ('2023-09-17', 50.00, 5),
  ('2023-09-18', 50.00, 5),
  ('2023-09-19', 50.00, 5),
  ('2023-09-20', 50.00, 5),
  ('2024-02-10', 50.00, 6),
  ('2024-02-11', 50.00, 6),
  ('2024-02-12', 50.00, 6),
  ('2024-02-13', 50.00, 6),
  ('2024-02-14', 50.00, 6),
  ('2024-02-15', 50.00, 6),
  ('2024-02-16', 50.00, 6),
  ('2024-02-17', 50.00, 6),
  ('2024-02-18', 50.00, 6),
  ('2024-02-19', 50.00, 6);


DELIMITER //

CREATE PROCEDURE InsertAvailabilityInRange(
    IN startDate DATE,
    IN endDate DATE,
    IN price DECIMAL(20, 2),
    IN listingId INT
)
BEGIN
    WHILE startDate <= endDate DO
        INSERT INTO Availability (dateAvailable, price, listingId)
        VALUES (startDate, price, listingId);
        
        SET startDate = DATE_ADD(startDate, INTERVAL 1 DAY);
    END WHILE;
END;
//

DELIMITER ;


CALL InsertAvailabilityInRange('2024-02-20', '2024-03-05', 70.00, 6);



INSERT INTO BookedBy (listingId, renterSIN, startDate, endDate, isCancelled, cancelledBy)
VALUES
  (1, 646456643, '2023-08-01', '2023-08-05', 0, NULL),
  (2, 563533452, '2023-12-19', '2023-12-19', 0, NULL),
  (5,	563533452,	'2023-09-17',	'2023-09-20',	0, NULL);


-- Update isAvailable to 0 for Listing 1
UPDATE Availability SET isAvailable = 0 WHERE listingId = 1 AND dateAvailable BETWEEN '2023-08-01' AND '2023-08-05';
UPDATE Availability SET isAvailable = 0 WHERE listingId = 2 AND dateAvailable BETWEEN '2023-12-19' AND '2023-12-19';
UPDATE Availability SET isAvailable = 0 WHERE listingId = 5 AND dateAvailable BETWEEN '2023-09-17' AND '2023-09-20';


INSERT INTO Amenities (name, price) VALUES ('Hair dryer', 5.00);
INSERT INTO Amenities (name, price) VALUES ('Cleaning products', 3.50);
INSERT INTO Amenities (name, price) VALUES ('Shampoo', 4.00);
INSERT INTO Amenities (name, price) VALUES ('Conditioner', 4.00);
INSERT INTO Amenities (name, price) VALUES ('Body soap', 3.00);
INSERT INTO Amenities (name, price) VALUES ('Shower gel', 4.50);
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

-- Listing 1 amenities
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Hair dryer');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Cleaning products');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Shampoo');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Conditioner');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Body soap');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Shower gel');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Towels, bed sheets, soap, and toilet paper');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Hangers');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (1, 'Bed linens');
-- Add more amenities for listing 1

-- Listing 2 amenities
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (2, 'Hair dryer');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (2, 'Shampoo');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (2, 'Towels, bed sheets, soap, and toilet paper');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (2, 'Fast wifi');
-- Add more amenities for listing 2

-- Listing 3 amenities
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (3, 'Hair dryer');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (3, 'Cleaning products');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (3, 'Shampoo');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (3, 'Conditioner');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (3, 'Body soap');
-- Add more amenities for listing 3

-- Listing 4 amenities
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (4, 'Hair dryer');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (4, 'Cleaning products');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (4, 'Shampoo');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (4, 'Conditioner');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (4, 'Body soap');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (4, 'Shower gel');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (4, 'Towels, bed sheets, soap, and toilet paper');
-- Add more amenities for listing 4

-- Listing 5 amenities
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (5, 'Hair dryer');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (5, 'Cleaning products');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (5, 'Shampoo');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (5, 'Conditioner');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (5, 'Body soap');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (5, 'Shower gel');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (5, 'Towels, bed sheets, soap, and toilet paper');
INSERT INTO ListingToAmenities (listingId, amenity) VALUES (5, 'Hangers');
-- Add more amenities for listing 5
INSERT INTO ListingToAmenities (listingId, amenity) VALUES
(6,	'Body soap'),
(6,	'Conditioner'),
(6,	'Fast wifi'),
(6,	'Hair dryer'),
(6,	'Iron'),
(6,	'Oven'),
(6,	'Microwave'),
(6,	'Toaster'),
(6,	'Towels, bed sheets, soap, and toilet paper');




