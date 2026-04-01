import pandas as pd
import os

# Paths
RAW_CSV = 'IIoT_Smart_Parking_Management.csv'
CSV_DIR = 'csv'
os.makedirs(CSV_DIR, exist_ok=True)

# Load raw data
df = pd.read_csv(RAW_CSV)

# ParkingLot CSV
parking_lots = df[['Parking_Lot_Section']].drop_duplicates().reset_index(drop=True)
parking_lots['LotID'] = parking_lots.index + 1  # auto-generate LotID
parking_lots = parking_lots.rename(columns={'Parking_Lot_Section': 'Zone'})
parking_lots.to_csv(os.path.join(CSV_DIR, 'ParkingLot.csv'), index=False)

# Driver CSV
drivers = df[['User_Type']].drop_duplicates().reset_index(drop=True)
drivers['DriverID'] = drivers.index + 1
drivers = drivers.rename(columns={'User_Type': 'UserType'})
drivers.to_csv(os.path.join(CSV_DIR, 'Driver.csv'), index=False)

# Helper mappings
lot_map = dict(zip(parking_lots['Zone'], parking_lots['LotID']))
driver_map = dict(zip(drivers['UserType'], drivers['DriverID']))

# ParkingSpot CSV
spots = df[['Parking_Spot_ID','Spot_Size','Occupancy_Status','Parking_Lot_Section']].drop_duplicates().reset_index(drop=True)
spots['LotID'] = spots['Parking_Lot_Section'].map(lambda x: lot_map.get(x, 1))  # default LotID=1
spots = spots.rename(columns={'Spot_Size':'SpotType','Occupancy_Status':'Status','Parking_Spot_ID':'SpotID'})
spots = spots[['SpotID','SpotType','Status','LotID']]
spots.to_csv(os.path.join(CSV_DIR, 'ParkingSpot.csv'), index=False)

# Sensor CSV
sensors = df[['Parking_Spot_ID']].drop_duplicates().rename(columns={'Parking_Spot_ID':'SpotID'})
sensors.to_csv(os.path.join(CSV_DIR, 'Sensor.csv'), index=False)

# Reservation
reservations = df[df['Reserved_Status'].notna()][['Entry_Time','Exit_Time','Reserved_Status','User_Type','Parking_Spot_ID']].copy()
reservations['DriverID'] = reservations['User_Type'].map(driver_map)
reservations = reservations.rename(columns={'Entry_Time':'StartTime','Exit_Time':'EndTime','Reserved_Status':'Status','Parking_Spot_ID':'SpotID'})
reservations = reservations[['StartTime','EndTime','Status','DriverID','SpotID']]
reservations.to_csv(os.path.join(CSV_DIR, 'Reservation.csv'), index=False)

# ParkingEvent
events = df[df['Entry_Time'].notna()][['Entry_Time','Exit_Time','Payment_Amount','User_Type','Parking_Spot_ID']].copy()
events['DriverID'] = events['User_Type'].map(driver_map)
events = events.rename(columns={'Entry_Time':'EntryTime','Exit_Time':'ExitTime','Payment_Amount':'FeeCharged','Parking_Spot_ID':'SpotID'})
events = events[['EntryTime','ExitTime','FeeCharged','DriverID','SpotID']]
events.to_csv(os.path.join(CSV_DIR, 'ParkingEvent.csv'), index=False)

# AvailabilityRecord
availability = df[df['Timestamp'].notna()][['Parking_Spot_ID','Timestamp','Occupancy_Status']].copy()
availability = availability.rename(columns={'Parking_Spot_ID':'SpotID','Timestamp':'RecordTimestamp','Occupancy_Status':'AvailabilityStatus'})
availability.to_csv(os.path.join(CSV_DIR, 'AvailabilityRecord.csv'), index=False)

print("[INFO] All CSV files generated in 'csv/' folder.")