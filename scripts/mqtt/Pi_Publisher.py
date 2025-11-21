# Paho PQTT library implements a client class that can be used to add MQTT to support Python program
import paho.mqtt.client as mqtt
# necessary for compatibility with paho-mqtt version 2.0+
from paho.mqtt.client import CallbackAPIVersion
import time
from datetime import datetime


broker = "localhost"    # tells client to look for MQTT broker (Mosquitto) on the same machine (RPi)
topic = "command/esp32"    # MQTT topic that client will subscribe to, same topic ESP32 publishes to
client_id = "Client1"
publish_interval = 5    # seconds

# called when the client connects to the broker
# reason_code is the status code from the broker
def on_connect(client, userdata, flags, reason_code, properties):
    if (reason_code == 0):        # reason_code: 0, client is successfully connected
        print("Connected to MQTT broker!")
    
    else:                         # reason_code: 1, connection failure
        print(f"Failed to connect, connection status {reason_code}")

# Generate and publish the message
def publish_command(client):
    # Dynamic message: current time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = f"Message from Pi at: {timestamp}" 
    
    # QoS 1 ensures the message is delivered at least once
    client.publish(topic, payload, qos=1, retain=False) 
    
    print(f"\n PUBLISHED:")
    print(f"   Topic='{topic}'")
    print(f"   Payload='{payload}'")


# Paho's internal error handling when client attempts to connect or reconnect to the MQTT broker
# used when using background network loop functions like client.loop_start()
def on_connect_fail(client, userdata):
    print("Connection failed, Paho will retry..")
    
# create MQTT client instance
# "PythonListener" is the unique Client ID used to identify this subscriber to the MQTT broker
client = mqtt.Client(CallbackAPIVersion.VERSION2, "Client1")
# assigns the connection handler
client.on_connect = on_connect
# assign the handler
client.on_connect_fail = on_connect_fail

# connect to broker and start listening
print("Connecting to broker...")
client.connect(broker, 1883, 60)    # port 1883 (standard MQTT port)
                                    # keep-alive timeout of 60 seconds

# 1. Start the network loop in a background thread
# This keeps the connection alive, sends keep-alives, and handles protocol tasks
client.loop_start()

# 2. Main program loop for periodic publishing
try:
    print(f"Starting continuous publishing every {publish_interval} seconds...")
    while True:
        # Call the publishing function
        publish_command(client)
        # Wait for the specified interval
        time.sleep(publish_interval)

except KeyboardInterrupt:
    print("\n Publisher script stopped by user.")

# guarantee cleanup code is executed before program terminates
finally:
    # 3. Stop the loop and disconnect cleanly
    client.loop_stop()
    client.disconnect() # <-- must run even if Ctrl+C is pressed
    print("Clean disconnect.")
