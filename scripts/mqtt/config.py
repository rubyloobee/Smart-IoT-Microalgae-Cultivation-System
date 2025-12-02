# Constants for MQTT Client configuration and topics.

# --- Network Configuration ---
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883           # standard MQTT port
KEEP_ALIVE_SEC = 60          # keep-alive timeout of 60 seconds

# --- Topics ---
# The Pi will subscribe to this topic to receive status updates from the ESP32.
TOPIC_SUBSCRIBE = "status/esp32"

# The Pi will publish commands/data to this topic (not used in this combined file, 
# but included for future modularity if the Pi became a dedicated publisher).
TOPIC_PUBLISH = "command/esp32"

# --- Client Settings ---
CLIENT_ID = "Pi_BiDir_Client"
PUBLISH_INTERVAL_SEC = 20