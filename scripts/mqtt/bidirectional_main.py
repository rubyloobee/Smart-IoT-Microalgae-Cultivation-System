# Paho PQTT library implements a client class that can be used to add MQTT to support Python program
import paho.mqtt.client as mqtt
# necessary for compatibility with paho-mqtt version 2.0+
from paho.mqtt.client import CallbackAPIVersion
import time

# Import configuration and handler functions
from config import *
from subscriber import on_message
from publisher import publish_status

# --- Connection Handlers ---
# called when the client connects to the broker
# Handles connection acceptance/rejection and sets up subscriptions
# reason_code is the status code from the broker
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connecting to MQTT...")
    if reason_code == 0:      # reason_code: 0, client is successfully connected
        print("MQTT connected!")
        
        # 1. SUBSCRIBER SETUP: Subscribe to the topic the ESP32 publishes status to
        client.subscribe(TOPIC_SUBSCRIBE, qos=1)   
        print(f"\nSubscribed to topic: {TOPIC_SUBSCRIBE}")
    else:                     # reason_code: 1, connection failure  
        print(f"Failed to subscribe, reason code = {reason_code}")
        
# Paho's internal error handling when client attempts to connect or reconnect to the MQTT broker
# used when using background network loop functions like client.loop_start() / client.loop_forever()
def on_connect_fail(client, userdata):
    print("Connection failed, Paho will retry...")
    
# --- Main Execution ---

# Create MQTT client instance (using V2 API)
client = mqtt.Client(CallbackAPIVersion.VERSION2, CLIENT_ID)

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
    print(f"\nStarting continuous publishing every {PUBLISH_INTERVAL_SEC} seconds...")
    while True:
        # Publish messages from the Pi to the ESP32
        publish_status(client) 
        
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