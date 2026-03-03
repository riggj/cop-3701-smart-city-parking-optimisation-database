-- =====================================================
-- SMART PARKING MANAGEMENT SYSTEM
-- CSV-ALIGNED & BCNF NORMALIZED
-- =====================================================

CREATE DATABASE IF NOT EXISTS smart_parking;
USE smart_parking;

-- =====================================================
-- DROP EXISTING TABLES
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS AvailabilityRecord;
DROP TABLE IF EXISTS ParkingEvent;
DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS Sensor;
DROP TABLE IF EXISTS Driver;
DROP TABLE IF EXISTS ParkingSpot;
DROP TABLE IF EXISTS ParkingLot;
DROP TABLE IF EXISTS ParkingData_Staging;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- STAGING TABLE
-- =====================================================
CREATE TABLE ParkingData_Staging (
    Timestamp DATETIME,
    Parking_Spot_ID INT,
    Entry_Time DATETIME,
    Exit_Time DATETIME,
    Reserved_Status VARCHAR(50),
    Payment_Amount DECIMAL(10,2),
    Parking_Lot_Section VARCHAR(50),
    Occupancy_Status VARCHAR(50),
    Spot_Size VARCHAR(50),
    User_Type VARCHAR(50)
);

-- Load CSV into staging (relative path)
LOAD DATA LOCAL INFILE 'IIoT_Smart_Parking_Management.csv'
INTO TABLE ParkingData_Staging
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- =====================================================
-- NORMALIZED TABLES (BCNF)
-- =====================================================
CREATE TABLE ParkingLot (
    LotID INT PRIMARY KEY AUTO_INCREMENT,
    Zone VARCHAR(50) UNIQUE
);

CREATE TABLE ParkingSpot (
    SpotID INT PRIMARY KEY,
    SpotType VARCHAR(50),
    Status VARCHAR(50),
    LotID INT NOT NULL,
    FOREIGN KEY (LotID) REFERENCES ParkingLot(LotID)
);

CREATE TABLE Driver (
    DriverID INT PRIMARY KEY AUTO_INCREMENT,
    UserType VARCHAR(50) UNIQUE
);

CREATE TABLE Sensor (
    SensorID INT PRIMARY KEY AUTO_INCREMENT,
    SpotID INT UNIQUE,
    FOREIGN KEY (SpotID) REFERENCES ParkingSpot(SpotID)
);

CREATE TABLE Reservation (
    ReservationID INT PRIMARY KEY AUTO_INCREMENT,
    StartTime DATETIME,
    EndTime DATETIME,
    Status VARCHAR(50),
    DriverID INT,
    SpotID INT,
    FOREIGN KEY (DriverID) REFERENCES Driver(DriverID),
    FOREIGN KEY (SpotID) REFERENCES ParkingSpot(SpotID)
);

CREATE TABLE ParkingEvent (
    EventID INT PRIMARY KEY AUTO_INCREMENT,
    EntryTime DATETIME,
    ExitTime DATETIME,
    FeeCharged DECIMAL(10,2),
    DriverID INT,
    SpotID INT,
    FOREIGN KEY (DriverID) REFERENCES Driver(DriverID),
    FOREIGN KEY (SpotID) REFERENCES ParkingSpot(SpotID)
);

CREATE TABLE AvailabilityRecord (
    SpotID INT,
    RecordTimestamp DATETIME,
    AvailabilityStatus VARCHAR(50),
    PRIMARY KEY (SpotID, RecordTimestamp),
    FOREIGN KEY (SpotID) REFERENCES ParkingSpot(SpotID)
);

-- =====================================================
-- POPULATE NORMALIZED TABLES
-- =====================================================

-- Insert all lots
INSERT INTO ParkingLot (Zone)
SELECT DISTINCT Parking_Lot_Section
FROM ParkingData_Staging
WHERE Parking_Lot_Section IS NOT NULL
  AND Parking_Lot_Section NOT IN (SELECT Zone FROM ParkingLot);

-- Insert a default lot for any missing spots
INSERT INTO ParkingLot (Zone)
SELECT 'DEFAULT_LOT'
WHERE NOT EXISTS (SELECT 1 FROM ParkingLot WHERE Zone='DEFAULT_LOT');

-- Insert all parking spots
INSERT INTO ParkingSpot (SpotID, SpotType, Status, LotID)
SELECT DISTINCT
    s.Parking_Spot_ID,
    s.Spot_Size,
    s.Occupancy_Status,
    COALESCE(l.LotID, (SELECT LotID FROM ParkingLot WHERE Zone='DEFAULT_LOT'))
FROM ParkingData_Staging s
LEFT JOIN ParkingLot l
ON s.Parking_Lot_Section = l.Zone
WHERE s.Parking_Spot_ID NOT IN (SELECT SpotID FROM ParkingSpot);

-- Insert Drivers
INSERT INTO Driver (UserType)
SELECT DISTINCT User_Type
FROM ParkingData_Staging
WHERE User_Type IS NOT NULL
  AND User_Type NOT IN (SELECT UserType FROM Driver);

-- Insert Sensors (1 per spot)
INSERT INTO Sensor (SpotID)
SELECT DISTINCT Parking_Spot_ID
FROM ParkingData_Staging
WHERE Parking_Spot_ID IN (SELECT SpotID FROM ParkingSpot)
  AND Parking_Spot_ID NOT IN (SELECT SpotID FROM Sensor);

-- Insert Reservations
INSERT INTO Reservation (StartTime, EndTime, Status, DriverID, SpotID)
SELECT
    s.Entry_Time,
    s.Exit_Time,
    s.Reserved_Status,
    d.DriverID,
    s.Parking_Spot_ID
FROM ParkingData_Staging s
JOIN Driver d ON s.User_Type = d.UserType
WHERE s.Reserved_Status IS NOT NULL
  AND s.Parking_Spot_ID IN (SELECT SpotID FROM ParkingSpot);

-- Insert Parking Events
INSERT INTO ParkingEvent (EntryTime, ExitTime, FeeCharged, DriverID, SpotID)
SELECT
    s.Entry_Time,
    s.Exit_Time,
    s.Payment_Amount,
    d.DriverID,
    s.Parking_Spot_ID
FROM ParkingData_Staging s
JOIN Driver d ON s.User_Type = d.UserType
WHERE s.Entry_Time IS NOT NULL
  AND s.Parking_Spot_ID IN (SELECT SpotID FROM ParkingSpot);

-- Insert Availability Records
INSERT INTO AvailabilityRecord (SpotID, RecordTimestamp, AvailabilityStatus)
SELECT
    Parking_Spot_ID,
    Timestamp,
    Occupancy_Status
FROM ParkingData_Staging
WHERE Timestamp IS NOT NULL
  AND Parking_Spot_ID IN (SELECT SpotID FROM ParkingSpot);

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT COUNT(*) AS ParkingLotCount FROM ParkingLot;
SELECT COUNT(*) AS ParkingSpotCount FROM ParkingSpot;
SELECT COUNT(*) AS DriverCount FROM Driver;
SELECT COUNT(*) AS SensorCount FROM Sensor;
SELECT COUNT(*) AS ReservationCount FROM Reservation;
SELECT COUNT(*) AS ParkingEventCount FROM ParkingEvent;
SELECT COUNT(*) AS AvailabilityRecordCount FROM AvailabilityRecord;