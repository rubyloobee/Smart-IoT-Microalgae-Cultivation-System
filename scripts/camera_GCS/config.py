# --- Camera & File System Configuration ---
# 1. Path where images are saved locally on the Raspberry Pi
SAVE_PATH = "/home/bee/Camera_GCS/images/"

# 2. Capture interval in seconds
INTERVAL_SECONDS = 60

# --- Google Cloud Storage Configuration ---
# 3. Path to Service Account JSON key file
CREDENTIALS_FILE = '/home/bee/Camera_GCS/microalgae-pics-3a919eb92020.json'

# 4. Unique name of the bucket created in Google Cloud Storage
BUCKET_NAME = 'rpi-gcs-pics'