# Paho PQTT library implements a client class that can be used to add MQTT to support Python program
import paho.mqtt.client as mqtt

# Called when a message is received from the broker
# msg is the object containing the message details
def on_message(client, userdata, msg):
    """Processes incoming MQTT messages."""
    
    print(f"\n>>> Message received from ESP32 >>>")
    # topic attribute within msg.topic is the default variable name used by
    # Paho-MQTT library to store topic string associated with the received message
    print(f"Topic: {msg.topic}")               
    # MQTT Payload (message content) is bytes, decode to a string for printing
    print(f"Payload: {msg.payload.decode()}")  