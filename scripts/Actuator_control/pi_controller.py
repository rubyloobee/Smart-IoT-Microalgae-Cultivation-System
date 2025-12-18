import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import firebase_admin
from firebase_admin import credentials, firestore
import json, time
from config import *
from log_scheduler import LoggingScheduler

# --- Initialization ---
# Load the credentials file
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    
db = firestore.client()

# Create MQTT client instance (using V2 API)
client = mqtt.Client(CallbackAPIVersion.VERSION2)

# --- Global State Memory ---
last_known_control = {}
last_known_log = {}

# --- Connection Handlers ---
# called when the client connects to the broker
# Handles connection acceptance/rejection and sets up subscriptions
# reason_code is the status code from the broker
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT Broker with code: {reason_code}")
    
# Paho's internal error handling when client attempts to connect or reconnect to the MQTT broker
# used when using background network loop functions like client.loop_start() / client.loop_forever()
def on_connect_fail(client, userdata):
    print("Connection failed, Paho will retry...")

# Assign handlers
client.on_connect = on_connect
client.on_connect_fail = on_connect_fail

# --- COLD START FUNCTION ---
def sync_on_startup():
    """Fetches control settings on boot."""
    print("Performing Cold Start sync...")
    
    global last_known_control, last_known_log
    
    # 1. Sync actuator control
    # Get all documents in the 'system_controls' collection
    control_docs = db.collection("system_controls").stream()
    for doc in control_docs:
        system_id = doc.id
        data = doc.to_dict() # Converts the NoSQL data to a Python dictionary
        
        # Fill 'memory' to prevent listener from double-sending
        last_known_control[system_id] = data
    
        # Extract all control parameters 
        payload = {
            "type": "FULL_SYNC",  # Tells ESP32 to update all control parameters
            "target_light_duration": data.get('target_light_duration'),
            "target_light_intensity": data.get('target_light_intensity'),
            "target_stirring_speed": data.get('target_stirring_speed'),
            "target_water_level": data.get('target_water_level')
        }
        
        # Publish to system-specific topic
        topic = f"{system_id}/control"
        client.publish(topic, json.dumps(payload), qos=1, retain=True)
        
        print(f"Initialized & Synced {system_id} to {topic}")
        print(f"   Payload Sent: {payload}\n")
        
    # 1. Sync logging interval
    log_docs = db.collection("log_interval").stream()
    for doc in log_docs:
        system_id = doc.id
        data = doc.to_dict() # Converts the NoSQL data to a Python dictionary
        
        # Fill 'memory' to prevent listener from double-sending
        last_known_log[system_id] = data
        
        print(f"Synced Logging Config for {system_id}:")
        print(f"   - Primary Interval : {data.get('primary_log_interval')}s")
        print(f"   - Sampling Interval: {data.get('sampling_log_interval')}s\n")

# --- DETECT CHANGE IN CONTROL SETTINGS ---
def on_control_change(col_snapshot, changes, read_time):
    """Triggers if any control settings are modified."""
    global last_known_control
    for change in changes:
        if change.type.name == 'MODIFIED':
            system_id = change.document.id
            new_data = change.document.to_dict()
            old_data = last_known_control.get(system_id, {})
            
            # Find only the modified field
            diff = {"type": "UPDATE"} # Tells ESP32 this is a single control parameter change
            fields = ['target_light_duration','target_light_intensity','target_stirring_speed', 'target_water_level'] 
            
            for key in fields:
                if new_data.get(key) != old_data.get(key):
                    diff[key] = new_data.get(key)
            
            # Only publish if something changed
            if len(diff) > 1: 
                last_known_control[system_id] = new_data
                topic = f"{system_id}/control"
                client.publish(topic, json.dumps(diff), qos=1)
                print(f"[Control Update] sent for {system_id}: {diff}\n")
            
# --- DETECT CHANGE IN LOGGING SETTINGS ---
def on_log_change(col_snapshot, changes, read_time):
    """Triggers if any logging settings are modified."""
    global last_known_log
    for change in changes:
        if change.type.name == 'MODIFIED':
            system_id = change.document.id
            new_data = change.document.to_dict()
            old_data = last_known_log.get(system_id, {})
            
            new_p = round(float(new_data.get('primary_log_interval', 0)), 1)
            new_s = round(float(new_data.get('sampling_log_interval', 0)), 1)
            
            old_p = round(float(old_data.get('primary_log_interval', 0)), 1)
            old_s = round(float(old_data.get('sampling_log_interval', 0)), 1)
            
            if new_p != old_p or new_s != old_s:
                # Update global memory
                last_known_log[system_id] = new_data
                
                print(f"[Logging Update] for {system_id}:")
                print(f"   - Primary : {old_p}s -> {new_p}s")
                print(f"   - Sampling: {old_s}s -> {new_s}s\n")
                
                # Ensure the Pi is running before reset the timer to count up to new interval
                if 'scheduler' in globals():
                    scheduler.next_primary[system_id] = time.time() + new_p
                    scheduler.next_sampling[system_id] = time.time() + new_s
            
            else:
                # Still update the memory to keep the timestamp current for the next check, 
                # but don't print or trigger the scheduler.
                last_known_log[system_id] = new_data

# --- Execution ---
client.connect(BROKER_ADDRESS, BROKER_PORT)
client.loop_start()

# Sync control parameters from before system shut down
sync_on_startup()

# Initialise scheduler
scheduler = LoggingScheduler(client, last_known_log)
# Start the background worker thread
scheduler.start()

# Watch for any changes in control/logging
query_watch_control = db.collection("system_controls").on_snapshot(on_control_change)
query_watch_log = db.collection("log_interval").on_snapshot(on_log_change)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    query_watch_control.unsubscribe()
    query_watch_log.unsubscribe()
    client.loop_stop()
    print("System Shutdown.")