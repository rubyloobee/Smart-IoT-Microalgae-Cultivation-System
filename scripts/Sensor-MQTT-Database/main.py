# Paho PQTT library implements a client class that can be used to add MQTT to support Python program
import paho.mqtt.client as mqtt
# necessary for compatibility with paho-mqtt version 2.0+
from paho.mqtt.client import CallbackAPIVersion
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Import configuration and handler functions
from config import *
from subscriber import on_message
from publisher import publish_status
from sqlite_handler import init_db

# --- Firebase Initialization ---
db = None
try:
    # 1. Load the credentials file
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    
    # 2. Check if Firebase is already initialized (important if using multiple modules)
    # Check if _apps list is empty
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("Firebase Admin SDK initialized.")
except Exception as e:
    print(f"Error initializing Firebase. Cloud upload will be skipped: {e}")

# --- Connection Handlers ---
# called when the client connects to the broker
# Handles connection acceptance/rejection and sets up subscriptions
# reason_code is the status code from the broker
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connecting to MQTT...")
    if reason_code == 0:      # reason_code: 0, client is successfully connected
        print("MQTT connected!")
        
        # 1. Define a list of topics and their QoS level
        # List format is: [(topic1, qos1), (topic2, qos2), ...]
        
        # Define QoS = 1 for both data streams to ensure delivery
        subscription_list = [
            (TOPIC_SUBSCRIBE_MAIN, 1),
            (TOPIC_SUBSCRIBE_SAMPLE, 1)
        ]
        
        # 2. Subscribe to the topics the ESP32 publishes data to
        client.subscribe(subscription_list)
        
        print(f"\nSuccessfully subscribed to the following topics:")
        for topic, qos in subscription_list:
            print(f"- {topic} (QoS: {qos})")
            
        # Pass the initialised Firestore client object via the userdata dictionary
        userdata['db_client'] = db 
        client.user_data_set(userdata)
        
        
    else:                     # reason_code: 1, connection failure  
        print(f"Failed to subscribe, reason code = {reason_code}")
        
# Paho's internal error handling when client attempts to connect or reconnect to the MQTT broker
# used when using background network loop functions like client.loop_start() / client.loop_forever()
def on_connect_fail(client, userdata):
    print("Connection failed, Paho will retry...")
    
# --- Main Execution ---
# Initialise local database
init_db()

# # Create a dictionary to hold user data (like the Firestore client)
# # This ensures userdata is never None when passed to callbacks
# client_userdata = {}

# Create MQTT client instance (using V2 API)
client = mqtt.Client(CallbackAPIVersion.VERSION2, CLIENT_ID, userdata={})

# Assign handlers
client.on_connect = on_connect
client.on_message = on_message
client.on_connect_fail = on_connect_fail

# Connect to broker and start listening
print("Connecting to broker...")
client.connect(BROKER_ADDRESS, BROKER_PORT, KEEP_ALIVE_SEC)  # port 1883 (standard MQTT port)
                                                             # kepp-alive timeout of 60 seconds

# 1. Start the network loop in a background thread
# This keeps the connection alive, sends keep-alives, and handles protocol tasks (Pub/Sub)
client.loop_start()

# 2. Main program loop for periodic publishing
try:
#     print(f"\nStarting continuous publishing every {PUBLISH_INTERVAL_SEC} seconds...")
    while True:
        # PublisRRRh messages from the Pi to the ESP32
#         publish_status(client) 
        
        # Wait for the specified interval
        time.sleep(PUBLISH_INTERVAL_SEC)

except KeyboardInterrupt:
    print("\nPublisher script stopped by user.")

# Guarantee cleanup code is executed before program terminates
finally:
    # 3. Stop the loop and disconnect cleanly
    client.loop_stop()
    client.disconnect()  # <-- must run even if Ctrl+C is pressed
    print("\nClean disconnect.")