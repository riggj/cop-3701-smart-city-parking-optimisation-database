CREATE DATABASE IF NOT EXISTS smart_parking;
USE smart_parking;

-- drop existing tables
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS AvailabilityRecord;
DROP TABLE IF EXISTS ParkingEvent;
DROP TABLE IF EXISTS Reservation;
DROP TABLE IF EXISTS Sensor;
DROP TABLE IF EXISTS Driver;
DROP TABLE IF EXISTS ParkingSpot;
DROP TABLE IF EXISTS ParkingLot;

SET FOREIGN_KEY_CHECKS = 1;

-- NORMALIZED TABLES (BCNF)
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