# Smart City Parking Optimization Database

This project is a design for a database system by which cars can find parking spots that are historically more likely to be available at given times. It will do this by taking into account historical data for a given parking spot including reservations, parking times, and usage patterns. This allows for further analysis, including peak hours, high-demand days, seasonal trends, and long-term usage behavior. 

The database supports both operational functionality (for example, reservations and parking events) and analytical functionality (for example, identifying peak congestion periods and frequently available spots).

Data source: http://kaggle.com/datasets/datasetengineer/smart-parking-management-dataset

To run this, you need to have MySQL installed, clone this repo and run `"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" --local-infile=1 -u root -p` (You may need to adgust the path to fit your needs). You'll be prompted with `mysql>` in your terminal. From there, run `SOURCE database.sql;`. This will ensure the data is loaded onto your device and you'll be able to run queries on it as you wish.'

I began this project not knowing that MySQL says "bye" when you run `exit`.