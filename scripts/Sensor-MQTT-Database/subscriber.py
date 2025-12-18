# Paho PQTT library implements a client class that can be used to add MQTT to support Python program
import paho.mqtt.client as mqtt
# Importing config for topics
from config import (
    TOPIC_SUBSCRIBE_MAIN, TOPIC_SUBSCRIBE_SAMPLE,
    MAIN_TANK_COLLECTION, SAMPLING_TANK_COLLECTION
)
import json
from sqlite_handler import insert_main_data, insert_sampling_data, update_upload_flag, fetch_unuploaded_data

def upload_to_firestore(db, collection_name, data):
    """Attempts to upload a single record to Firestore."""
    try:
        doc_id = data.get('timestamp') 

        # Creates copy of original sensor dictionary to prevent unintentionally altering the original dictionary
        upload_data = data.copy()
        
        # Remove redundant 'uploaded' field when uploading to cloud database
        upload_data.pop('uploaded', None)

        # Upload using the timestamp as the document ID
        db.collection(collection_name).document(doc_id).set(upload_data)
        
        print(f"-> Successfully uploaded record {doc_id} to Firestore collection {collection_name}")
        return True

    except Exception as e:
        print(f"Error uploading to Firestore collection {collection_name}: {e}")
        return False

# Called when a message is received from the broker
# msg is the object containing the message details
def on_message(client, userdata, msg):
    """Processes incoming MQTT messages."""
    
    # Retrieve the initialised Firestore client object
    db = userdata.get('db_client')
    
    # MQTT Payload (message content) is bytes, decode to a string for printing
    payload_str = msg.payload.decode()
    
    print(f"\n>>> Message received from ESP32 >>>")
    # topic attribute within msg.topic is the default variable name used by
    # Paho-MQTT library to store topic string associated with the received message
    print(f"Topic: {msg.topic}")               
    print(f"Payload: {payload_str}")
    
    # Parse the JSON string into a Python Dictionary
    # Allow access of any specific sensor reading using its key (sensor name)
    data = json.loads(payload_str)
    
    local_success = False
    collection = None
    
    # --- ACTIONS BASED ON TOPIC ---
    if msg.topic == TOPIC_SUBSCRIBE_MAIN:
        print("-> Actions to log main tank data...")
        local_success = insert_main_data(data)
        collection = MAIN_TANK_COLLECTION
        
        
    elif msg.topic == TOPIC_SUBSCRIBE_SAMPLE:
        print("-> Actions to log sample tank data...")
        local_success = insert_sampling_data(data)
        collection = SAMPLING_TANK_COLLECTION
        
    # --- IMMEDIATE CLOUD UPLOAD ATTEMPT  ---
    # if initialisation of db is successful, and local database upload is successful
    if db and local_success:
        cloud_success = upload_to_firestore(db, collection, data)
        
        if cloud_success:
            update_upload_flag(data.get('timestamp'))
            
def process_and_upload_backlog(db_client):
    """
    Checks the local database for unuploaded records and attempts to upload them.
    Implements the 'Store-and-Forward' pattern.
    """
    # Use the initialised Firestore client object
    if not db_client:
        print("Skipping backlog upload: Firestore client is not initialized.")
        return
        
    print("\n--- Checking for unuploaded data (backlog) ---")
    
    # 1. Fetch all records with uploaded = 0
    backlog = fetch_unuploaded_data()
    
    uploaded_count = 0
    
    # 2. Iterate through main tank backlog
    for record in backlog['main_tank']:
        # Attempt to upload to Firestore
        if upload_to_firestore(db_client, MAIN_TANK_COLLECTION, record):
            # If successful, update the local database flag to 1
            # The timestamp is the key to update the flag
            update_upload_flag(record.get('timestamp'))
            uploaded_count += 1
            
    # 3. Iterate through sampling tank backlog
    for record in backlog['sampling_tank']:
        # Attempt to upload to Firestore
        if upload_to_firestore(db_client, SAMPLING_TANK_COLLECTION, record):
            # If successful, update the local database flag to 1
            update_upload_flag(record.get('timestamp'))
            uploaded_count += 1
            
    if uploaded_count > 0:
        print(f"--- Backlog upload complete: {uploaded_count} records sent. ---")
    else:
        print("--- Backlog check complete: No unuploaded records found. ---")