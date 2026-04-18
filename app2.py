import oracledb

LIB_DIR = r"C:\Users\jwhal\Oracle\instantclient_11_2\instantclient_23_0"  # Your Instant Client Path
DB_USER = "JWHALEN0130_SCHEMA_ZDAG9"
DB_PASS = "POS8$12OIN3K7M1UCY84L2237P8GaE"
DB_DSN  = "db.freesql.com" + ":" + "1521" + "/" + "23ai_34ui2"

oracledb.init_oracle_client(lib_dir=LIB_DIR)
db = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
cursor = db.cursor()

def print_results(cursor):
    columns = [col[0] for col in cursor.description]
    print("\n" + " | ".join(columns))
    print("-" * 50)

    for row in cursor:
        print(" | ".join(str(x) for x in row))
    print()

def reservations_between_dates(db):
    start = input("Enter start date (YYYY-MM-DD HH24:MI:SS): ")
    end = input("Enter end date (YYYY-MM-DD HH24:MI:SS): ")

    query = """
    SELECT * FROM RESERVATION
    WHERE STARTTIME >= TO_TIMESTAMP(:start_date, 'YYYY-MM-DD HH24:MI:SS')
    AND ENDTIME <= TO_TIMESTAMP(:end_date, 'YYYY-MM-DD HH24:MI:SS')
    """

    cur = db.cursor()
    cur.execute(query, {'start_date': start, 'end_date': end})
    print_results(cur)

def previous_parking_data(db):
    driver_id = input("Enter driver ID:")

    query = """
    SELECT pe.* FROM PARKINGEVENT pe
    JOIN DRIVER d
    ON pe.DRIVERID = d.DRIVERID
    WHERE d.DRIVERID = :driver_id
    """

    cur = db.cursor()
    cur.execute(query, {'driver_id': driver_id})
    print_results(cur)

def previous_reservation_spot(db):
    spot_id = input("Enter spot ID:")

    query = """
    SELECT * FROM RESERVATION r
    WHERE SPOTID = :spot_id
    ORDER BY STARTTIME DESC
    """

    cur = db.cursor()
    cur.execute(query, {'spot_id': spot_id})
    print_results(cur)

def no_reservations(db):
    query = """
    SELECT * FROM PARKINGSPOT sp
    WHERE sp.SPOTID NOT IN(
        SELECT r.SPOTID 
        FROM RESERVATION r
        WHERE r.STATUS = 'Active'
    )"""

    cur =  db.cursor()
    cur.execute(query)
    print_results(cur)

def filled(db):
    query = """
    SELECT sp.SPOTID FROM PARKINGSPOT sp
    JOIN RESERVATION r
    ON sp.SPOTID = r.SPOTID
    WHERE sp.STATUS = 'Occupied'
    """

    cur = db.cursor()
    cur.execute(query)
    print_results(cur)

def main():
    while True:
        print("1. Reservation between two dates")
        print("2. Previous parking data for a driver")
        print("3. Reservation data for a parking spot")
        print("4. Parking spots with no current reservations")
        print("5. Currently filled parking spots")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            reservations_between_dates(db)
        elif choice == "2":
            previous_parking_data(db)
        elif choice == "3":
            previous_reservation_spot(db)
        elif choice == "4":
            no_reservations(db)
        elif choice == "5":
            filled(db)
        elif choice == "6":
            print("Exiting program")
            break
        else:
            print("Invalid choice. Please try again.")
        
    cursor.close()
    db.close()

if __name__ == "__main__":
    main()
            

