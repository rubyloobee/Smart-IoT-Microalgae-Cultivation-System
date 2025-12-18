import time
import os
import subprocess
import config
from upload_to_gcs import upload_file_to_gcs

# Define camera settings for rpicam-still
WIDTH = 1280
HEIGHT = 720
TIME_OUT = 3000


# The main capture loop
while True:
    # Create unique filename
    filename = time.strftime(f"{config.SAVE_PATH}%Y%m%d_%H%M%S.jpg")
    
    #     # Construct the rpicam-still command
    command = [
        "rpicam-still","-t", str(TIME_OUT),
        "-o", filename,            # Output file path
    ]
    
#     # Construct the rpicam-still command
#     command = [
#         "rpicam-still",
#         "--width", str(WIDTH),
#         "--height", str(HEIGHT),
#         "--shutter", str(SHUTTER_SPEED), # Example: Use advanced camera settings
#         "--output", filename,            # Output file path
#         "--timeout", "1"                 # Wait for 1 millisecond before capture
#     ]

    print(f"Executing: {' '.join(command)}")
    
    # The run function executes the command and waits for it to complete
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print(f"Captured: {filename}")
    
    # Immediatly upload the captured image to GCS
    print(f"Attempting to upload: {os.path.basename(filename)}")
    success, url = upload_file_to_gcs(filename)

    # Wait for the next interval
    time.sleep(config.INTERVAL_SECONDS)
    
    
    
    
    