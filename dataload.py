import mysql.connector
import pandas as pd

db = mysql.connector.connect(
    host = "localhost",
    user = "K9xL2qR5v",
    password = "P7mK9xL2qR5vN3wJH8bF",
    database = "smart_parking"
)

cursor = db.cursor()

def load_csv(file, table):
    df = pd.read_csv(file)
    
    # Remove duplicates based on primary key columns
    if table == "ParkingSpot":
        df = df.drop_duplicates(subset=['SpotID'], keep='first')
    elif table == "Sensor":
        df = df.drop_duplicates(subset=['SpotID'], keep='first')
    elif table == "AvailabilityRecord":
        df = df.drop_duplicates(subset=['SpotID', 'RecordTimestamp'], keep='first')
    
    # Build column names and placeholders
    columns = ', '.join(df.columns)
    placeholders = ','.join(['%s'] * len(df.columns))
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    skipped = 0
    for idx, row in df.iterrows():
        try:
            cursor.execute(sql, tuple(row))
        except Exception as e:
            skipped += 1
    
    db.commit()
    if skipped > 0:
        print(f"{table} loaded ({len(df) - skipped} rows, {skipped} skipped)")
    else:
        print(f"{table} loaded")

# Clear existing data first (respecting foreign key dependencies)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("TRUNCATE TABLE AvailabilityRecord")
cursor.execute("TRUNCATE TABLE ParkingEvent")
cursor.execute("TRUNCATE TABLE Reservation")
cursor.execute("TRUNCATE TABLE Sensor")
cursor.execute("TRUNCATE TABLE ParkingSpot")
cursor.execute("TRUNCATE TABLE Driver")
cursor.execute("TRUNCATE TABLE ParkingLot")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# Load CSV files in order of foreign key dependencies
load_csv("csv/ParkingLot.csv", "ParkingLot")
load_csv("csv/Driver.csv", "Driver")
load_csv("csv/ParkingSpot.csv", "ParkingSpot")
load_csv("csv/Sensor.csv", "Sensor")
load_csv("csv/Reservation.csv", "Reservation")
load_csv("csv/ParkingEvent.csv", "ParkingEvent")
load_csv("csv/AvailabilityRecord.csv", "AvailabilityRecord")

cursor.close()
db.close()