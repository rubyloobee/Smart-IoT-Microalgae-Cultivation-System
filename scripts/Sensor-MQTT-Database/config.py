# Constants for MQTT Client configuration and topics.

# --- Network Configuration ---
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883           # standard MQTT port
KEEP_ALIVE_SEC = 60          # keep-alive timeout of 60 seconds

# --- SQLite Database Configuration ---
DB_NAME = "/home/bee/Sensor_MQTT_Firebase/algae_project.db"
BACKLOG_CHECK_INTERVAL_SEC = 20

# ---Firebase Configuration ---
# Path to Service Account JSON file (Used for authentication)
FIREBASE_CREDENTIALS_PATH = "/home/bee/Firebase/smart-microalgae-cultivation-firebase-adminsdk-fbsvc-9bbb9d4d62.json"
# Firestore collection path where the data should be saved
MAIN_TANK_COLLECTION = "main_tank_data"
SAMPLING_TANK_COLLECTION = "sampling_tank_data"

# --- Topics ---
# The Pi will subscribe to this topic to receive data from the ESP32.
TOPIC_SUBSCRIBE_MAIN = "main_tank/data"
TOPIC_SUBSCRIBE_SAMPLE = "sampling_tank/data"

# The Pi will publish commands/data to this topic (not used in this combined file, 
# but included for future modularity if the Pi became a dedicated publisher).
TOPIC_PUBLISH = "command/esp32"

# --- Client Settings ---
CLIENT_ID = "Pi_BiDir_Client"
#PUBLISH_INTERVAL_SEC = 20
