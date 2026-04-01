import mysql.connector
import pandas as pd
from db_config import DB_CONFIG  # import your private credentials

# --- MySQL Connection ---
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# --- Function to Load CSV into Table ---
def load_csv_to_table(csv_path, table_name, columns):
    df = pd.read_csv(csv_path)
    df = df.fillna('')  # replace NaN with empty string if needed
    for _, row in df.iterrows():
        values = tuple(row[col] for col in columns)
        placeholders = ','.join(['%s']*len(columns))
        sql = f"INSERT IGNORE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        cursor.execute(sql, values)
    conn.commit()
    print(f"[INFO] Loaded {len(df)} rows into {table_name}")

# --- Load Tables in Order ---
load_csv_to_table('csv/ParkingLot.csv', 'ParkingLot', ['Zone'])
load_csv_to_table('csv/Driver.csv', 'Driver', ['UserType'])
load_csv_to_table('csv/ParkingSpot.csv', 'ParkingSpot', ['SpotID','SpotType','Status','LotID'])
load_csv_to_table('csv/Sensor.csv', 'Sensor', ['SpotID'])
load_csv_to_table('csv/Reservation.csv', 'Reservation', ['StartTime','EndTime','Status','DriverID','SpotID'])
load_csv_to_table('csv/ParkingEvent.csv', 'ParkingEvent', ['EntryTime','ExitTime','FeeCharged','DriverID','SpotID'])
load_csv_to_table('csv/AvailabilityRecord.csv', 'AvailabilityRecord', ['SpotID','RecordTimestamp','AvailabilityStatus'])

# --- Close Connection ---
cursor.close()
conn.close()
print("[INFO] All CSV files loaded successfully.")