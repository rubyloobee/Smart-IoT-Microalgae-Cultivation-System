import sqlite3
from config import DB_NAME

def init_db():
    """Creates the tables if they don't exist."""
    try:
        # Conect with the database file, SQLite creates the file if it does not exist
        with sqlite3.connect(DB_NAME) as conn:
            # Cursor object as a pointer to execute SQL commands and retrieve results from database
            cursor = conn.cursor()
            
            # --- Main Tank Table ---
            # id INTEGER PRIMARY KEY AUTOINCREMENT: define a unique id for each row
            # TEXT: store the data as string
            # REAL: store the data as floating-point numbers
            # "uploaded": 0 - not uploaded/fail upload, 1 - uploaded
            # Pi periodically checks local database where uploaded = 0, push the backlog to Firestore (Store-and-Forward)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS main_tank_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT, 
                    temperature_C REAL,
                    light_intensity_lux REAL,
                    water_level_cm REAL,
                    pH_value REAL,
                    uploaded INTEGER DEFAULT 0
                )
            ''')

            # --- Sampling Tank Table ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sampling_tank_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    EC_value REAL,
                    uploaded INTEGER DEFAULT 0
                )
            ''')
            
            # Finalise the table changes/creations and make them permanent in database file
            conn.commit()
            print(f"Database '{DB_NAME}' initialized successfully.")
            return True
           
    # Only handle errors that are related to SQLite database operations
    except sqlite3.Error as e:
        print(f"Database error during init: {e}")
        return False

def insert_main_data(data_dict):
    """Inserts data into main_tank_logs using specific JSON keys."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            # Use data_dict.get() to safely retrieve values
            # If a key is missing in the JSON, it inserts None (NULL)
            # ? : parameter placeholders, indicate the actual values for insertion
            #     will be provided separately when SQL statement is executed
            cursor.execute('''
                INSERT INTO main_tank_logs (timestamp, temperature_C, light_intensity_lux, water_level_cm, pH_value)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data_dict.get('timestamp'), 
                data_dict.get('temperature_C'), 
                data_dict.get('light_intensity_lux'), 
                data_dict.get('water_level_cm'),
                data_dict.get('pH_value')
            ))
            conn.commit()
            print(f">> Saved Main Tank data: {data_dict.get('timestamp')}")
            return True
        
    except sqlite3.Error as e:
        print(f"Error inserting main data: {e}")
        return False

def insert_sampling_data(data_dict):
    """Inserts data into sampling_tank_logs using specific JSON keys."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sampling_tank_logs (timestamp, EC_value)
                VALUES (?, ?)
            ''', (
                data_dict.get('timestamp'), 
                data_dict.get('EC_value')
            ))
            conn.commit()
            print(f">> Saved Sampling Tank data: {data_dict.get('timestamp')}")
            return True
        
    except sqlite3.Error as e:
        print(f"Error inserting sampling data: {e}")
        return False
    
def update_upload_flag(timestamp):
    """Updates the uploaded flag to 1 for a given record."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            # Since the timestamp should be unique across both logs, we update both tables
            cursor.execute("UPDATE main_tank_logs SET uploaded = 1 WHERE timestamp = ?", (timestamp,))
            cursor.execute("UPDATE sampling_tank_logs SET uploaded = 1 WHERE timestamp = ?", (timestamp,))
            
            conn.commit()
            if cursor.rowcount > 0:
                print(f"-> Local upload flag set to 1 for timestamp: {timestamp}")

    except sqlite3.Error as e:
        print(f"Error updating upload flag: {e}")
        
def fetch_unuploaded_data():
    """Fetches all records from both logs where the 'uploaded' flag is 0."""
    unuploaded_records = {
        'main_tank': [],
        'sampling_tank': []
    }
    
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            
            # Fetch unuploaded main tank data
            cursor.execute("SELECT timestamp, temperature_C, light_intensity_lux, water_level_cm, pH_value FROM main_tank_logs WHERE uploaded = 0")
            # cursor.description contains column names with their desciption (display size, type code...)
            # Get column names to create dictionaries for easy use
            main_columns = [col[0] for col in cursor.description]
            # cursor.fetchall contains data values belonging to the column names
            for row in cursor.fetchall():
                # Convert the tuple row into a dictionary
                unuploaded_records['main_tank'].append(dict(zip(main_columns, row)))
            
            # Fetch unuploaded sampling tank data
            cursor.execute("SELECT timestamp, EC_value FROM sampling_tank_logs WHERE uploaded = 0")
            sampling_columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                unuploaded_records['sampling_tank'].append(dict(zip(sampling_columns, row)))

    except sqlite3.Error as e:
        print(f"Error fetching unuploaded data: {e}")
        
    return unuploaded_records