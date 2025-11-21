import firebase_admin
import json
from firebase_admin import credentials, firestore
# --- CONFIGURATION ---

# 1. Path to your Service Account JSON file (Used for authentication)
SERVICE_ACCOUNT_FILE = "/home/bee/Firebase/smart-microalgae-cultivation-firebase-adminsdk-fbsvc-9bbb9d4d62.json"

# 2. Path to the JSON file you want to upload
JSON_FILE_PATH = "/home/bee/Firebase/sensor_data.json"

# 3. The Firestore path where the data should be saved.
#    In Firestore, this path must be a COLLECTION path for batch uploads.
#    Example: 'sensor_logs', 'users/user_id/data', etc.
DATABASE_PATH = "sensor_logs"


def upload_json_to_firestore():
    """Reads a JSON file and uploads its contents to the specified collection in Firebase Firestore."""
    try:
        # 1. Initialize the Firebase App
        cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
        
        # Check if _apps list is empty
        if not firebase_admin._apps:
            # Performs actual setup if Firebase is not initalised
            firebase_admin.initialize_app(cred)
            print("Firebase app initialized successfully.")
        
        # Get the Firestore client
        db = firestore.client()

        # 2. Load data from the local JSON file
        with open(JSON_FILE_PATH, 'r') as f:           # open the file for reading only
            data_to_upload = json.load(f)              # Python's built-in json module parse the JSON formatted text
                                                       # and convert it to native Python data structure
        print(f"Successfully loaded data from {JSON_FILE_PATH}")

        # 3. Determine the collection reference
        # We assume DATABASE_PATH is a collection path (e.g., "sensor_logs")
        collection_ref = db.collection(DATABASE_PATH)
        print(f"Targeting Firestore Collection: {DATABASE_PATH}")

        # 4. Upload the data based on its type (list or single object)
        if isinstance(data_to_upload, list):
            # If the JSON is a list (e.g., multiple sensor readings), upload each as a document
            print(f"Uploading {len(data_to_upload)} records as separate documents...")
            
            uploaded_count = 0
            for record in data_to_upload:
                # Use .add() which automatically generates a unique Document ID (like RTDB's .push())
                collection_ref.add(record)
                uploaded_count += 1
            
            print(f"\nSuccessfully uploaded {uploaded_count} records to collection '{DATABASE_PATH}'")

        elif isinstance(data_to_upload, dict):
            # If the JSON is a single object, upload it as a single document
            print("Uploading single object as a new document...")
            collection_ref.add(data_to_upload)
            print(f"\nSuccessfully uploaded one document to collection '{DATABASE_PATH}'")

        else:
            print(f"ERROR: Data type {type(data_to_upload)} in JSON file is not supported for upload.")
            return

    except FileNotFoundError:
        print("ERROR: Configuration or data file not found. Check SERVICE_ACCOUNT_FILE and JSON_FILE_PATH.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Main execution block
if __name__ == "__main__":
    upload_json_to_firestore()