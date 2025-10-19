# Paho PQTT library implements a client class that can be used to add MQTT to support Python program
import paho.mqtt.client as mqtt
# necessary for compatibility with paho-mqtt version 2.0+
from paho.mqtt.client import CallbackAPIVersion


broker = "localhost"    # tells client to look for MQTT broker (Mosquitto) on the same machine (RPi)
topic = "status/esp32"    # MQTT topic that client will subscribe to, same topic ESP32 publishes to
client_id = "Client1"

# called when the client connects to the broker
# reason_code is the status code from the broker

def on_connect(client, userdata, flags, reason_code, properties):
    if (reason_code == 0):        # reason_code: 0, client is successfully connected
        print("Connected to MQTT broker!")
        client.subscribe(topic, qos = 1)   # subscribe to topic defined earlier (test/topic)
                                           # all messages published to this topic will now be forwarded to this client by the broker
                                           # connect with high QoS of 1
        print(f"\nSubscribed to topic: {topic} with QoS 1")
    else:                         # reason_code: 1, connection failure
        print(f"Failed to connect, connection status {reason_code}")
        
# called when a message is received from the broker
# msg is the object containing the message details
def on_message(client, userdata, msg):
    print(f"\nMessage received:")
    print(f"Topic: {msg.topic}")               # prints the topic the message came from
    print(f"Payload: {msg.payload.decode()}")  # prints the actual message content (payload)
                                               # MQTT payloads are sent as bytes, .decode() converts them to a readable string

# Paho's internal error handling when client attempts to connect or reconnect to the MQTT broker
# used when using background network loop functions like client.loop_forever
def on_connect_fail(client, userdata):
    print("Connection failed, Paho will retry..")
    
# create MQTT client instance
# "PythonListener" is the unique Client ID used to identify this subscriber to the MQTT broker
client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id)
# assigns the connection handler
client.on_connect = on_connect
# assigns the message handler
client.on_message = on_message
# assign the handler
client.on_connect_fail = on_connect_fail

# connect to broker and start listening
print("Connecting to broker...")
client.connect(broker, 1883, 60)    # port 1883 (standard MQTT port)
                                    # keep-alive timeout of 60 seconds

# starts the network loop, blocking call that runs continuously, handling background tasks like receiving messages and sending keep-alive signals
# keep alive signals: confirm that the client and broker are still connected, even when no data is being sent
client.loop_forever()