# Paho PQTT library implements a client class that can be used to add MQTT to support Python program
import paho.mqtt.client as mqtt
from datetime import datetime
from config import TOPIC_PUBLISH # Importing config for topics

def publish_status(client):
    """Generates and publishes a time-stamped status message to the ESP32's topic."""
    
    # Check if connected before trying to publish (resilient publishing)
    if not client.is_connected():
        print("WARNING: Skipping publish - Client is disconnected.")
        return
        
    # Dynamic message: current time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Message published from Pi
    payload = f"Message from Pi at: {timestamp}" 
    
    # QoS 1 ensures the message is delivered reliably
    client.publish(TOPIC_PUBLISH, payload, qos=1, retain=False) 
    
    print(f"\n--- Publish message to ESP32 ---")
    print(f"Topic: {TOPIC_PUBLISH}")
    print(f"Payload: {payload}")