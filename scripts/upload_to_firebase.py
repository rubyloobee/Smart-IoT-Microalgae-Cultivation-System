import firebase_admin
import json
from firebase_admin import credentials, db   # credentials: module used to authenticate Raspberry Pi script as a trusted administrator
                                             # db: short for database, primary interface for reading and writing data to the Firebase Realtime Database

# --- CONFIGURATION ---

# 1. Path to your Service Account JSON file
SERVICE_ACCOUNT_FILE = "/home/bee/Firebase/smart-microalgae-cultivation-firebase-adminsdk-fbsvc-9bbb9d4d62.json"

# 2. Your Realtime Database URL
DATABASE_URL = "https://smart-microalgae-cultivation-default-rtdb.asia-southeast1.firebasedatabase.app"

# 3. Path to the JSON file you want to upload
JSON_FILE_PATH = "/home/bee/Firebase/sensor_data.json"

# 4. The database path where the data should be saved
#    - Use '/' to replace the entire database content (BE CAREFUL!)
#    - Use '/sensor_logs' to create a new key called 'sensor_logs'
#    - Use '/sensor_logs/batch_A' to specify a sub-node
DATABASE_PATH = "/sensor_logs"


def upload_json_to_firebase():
    """Reads a JSON file and uploads its contents to the specified path in Firebase RTDB."""
    try:
        # 1. Initialize the Firebase App using the service account credentials
        # initialising firebase app
        # brings SDK to life and establishes the connection to the project
        cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
        firebase_admin.initialize_app(cred, {        
            'databaseURL': DATABASE_URL
        })
        print("Firebase app initialized successfully.")

        # 2. Load data from the local JSON file
        with open(JSON_FILE_PATH, 'r') as f:   # open the file for reading only
            data_to_upload = json.load(f)      # Python's built-in json module parse the JSON formatted text
                                               # and convert it to native Python data structure
        print(f"Successfully loaded data from {JSON_FILE_PATH}")

        # 3. Get a reference to the database path
        ref = db.reference(DATABASE_PATH)

        # 4. Upload the data
        #    - Use .set() to overwrite the data at the path
        #    - Use .push() if you want Firebase to generate a unique, timestamped key for the data
        
        # We will use .set() to upload the entire JSON object to the specified path
        ref.set(data_to_upload)
        
        # If your JSON is an array of records and you want a unique key for each:
        # for record in data_to_upload:
        #     ref.push(record)

        print(f"\nData successfully uploaded to Firebase at path: {DATABASE_PATH}")
        
    except FileNotFoundError:
        print(f"ERROR: Configuration or data file not found. Check paths.")
    except Exception as e:
        print(f"An error occurred: {e}")

# when this script is run directly, Python sets the variable __name__ to the string "__main__"
# when another Python script imports this script, Python sets the variable __name__ to the name of module itself
# function is executed when script is run directly, and skipped when imported by another script
if __name__ == "__main__":
    upload_json_to_firebase()