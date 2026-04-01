import pandas as pd
import os

# initial definitions
RAW_CSV = 'IIoT_Smart_Parking_Management.csv'
CSV_DIR = 'csv'
os.makedirs(CSV_DIR, exist_ok=True)


def generate_parking_lots(df):

    lots = df[['Parking_Lot_Section']].drop_duplicates().reset_index(drop=True)
    lots['LotID'] = lots.index + 1
    
    lots = lots.rename(columns={
        'Parking_Lot_Section': 'Zone'
    })
    
    lots.to_csv(os.path.join(CSV_DIR, 'ParkingLot.csv'), index=False)
    return lots


def generate_drivers(df):

    drivers = df[['User_Type']].drop_duplicates().reset_index(drop=True)
    drivers['DriverID'] = drivers.index + 1
    
    drivers = drivers.rename(columns={
        'User_Type': 'UserType'
    })
    
    drivers.to_csv(os.path.join(CSV_DIR, 'Driver.csv'), index=False)
    return drivers


def generate_parking_spots(df, lot_map):

    spots = df[['Parking_Spot_ID', 'Spot_Size', 'Occupancy_Status', 'Parking_Lot_Section']].drop_duplicates()
    spots['LotID'] = spots['Parking_Lot_Section'].map(lambda x: lot_map.get(x, 1))  # default LotID=1

    spots = spots.rename(columns={
        'Parking_Spot_ID':  'SpotID',
        'Spot_Size':        'SpotType',
        'Occupancy_Status': 'Status'
    })
    
    spots = spots[['SpotID', 'SpotType', 'Status', 'LotID']]
    spots.to_csv(os.path.join(CSV_DIR, 'ParkingSpot.csv'), index=False)
    return spots


def generate_sensors(spots):
    
    sensors = spots[['SpotID']].drop_duplicates()
    sensors.to_csv(os.path.join(CSV_DIR, 'Sensor.csv'), index=False)


def generate_reservations(df, driver_map):
    
    reservations = df[df['Reserved_Status'].notna()].copy()
    reservations['DriverID'] = reservations['User_Type'].map(driver_map)
    
    reservations = reservations.rename(columns={
        'Entry_Time':      'StartTime',
        'Exit_Time':       'EndTime',
        'Reserved_Status': 'Status',
        'Parking_Spot_ID': 'SpotID'
    })

    reservations = reservations[['StartTime', 'EndTime', 'Status', 'DriverID', 'SpotID']]
    reservations.to_csv(os.path.join(CSV_DIR, 'Reservation.csv'), index=False)


def generate_parking_events(df, driver_map):
    
    events = df[df['Entry_Time'].notna()].copy()
    events['DriverID'] = events['User_Type'].map(driver_map)
    
    events = events.rename(columns={
        'Entry_Time':      'EntryTime',
        'Exit_Time':       'ExitTime',
        'Payment_Amount':  'FeeCharged',
        'Parking_Spot_ID': 'SpotID'
    })
    
    events = events[['EntryTime', 'ExitTime', 'FeeCharged', 'DriverID', 'SpotID']]
    events.to_csv(os.path.join(CSV_DIR, 'ParkingEvent.csv'), index=False)


def generate_availabilities(df):
    
    availability = df[df['Timestamp'].notna()].copy()
    
    availability = availability.rename(columns={
        'Parking_Spot_ID':  'SpotID',
        'Timestamp':        'RecordTimestamp',
        'Occupancy_Status': 'AvailabilityStatus'
    })

    availability = availability[['SpotID', 'RecordTimestamp', 'AvailabilityStatus']]
    availability.to_csv(os.path.join(CSV_DIR, 'AvailabilityRecord.csv'), index=False)


def main():
    df = pd.read_csv(RAW_CSV)
    print("[INFO] Raw CSV loaded.")

    lots    = generate_parking_lots(df)
    drivers = generate_drivers(df)
    spots   = generate_parking_spots(df, dict(zip(lots['Zone'], lots['LotID'])))
    
    generate_sensors(spots)
    generate_reservations(df, dict(zip(drivers['UserType'], drivers['DriverID'])))
    generate_parking_events(df, dict(zip(drivers['UserType'], drivers['DriverID'])))
    generate_availabilities(df)

    print("[INFO] All normalized CSV files generated in 'csv/' folder.")


if __name__ == "__main__":
    main()