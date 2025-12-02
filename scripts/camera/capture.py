import time
from picamera2 import Picamera2

# Initialize camera and setup resolution
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (4056, 3040)})
picam2.configure(config)

# Define save path and interval (in seconds)
SAVE_PATH = "/home/bee/Camera/images/"
INTERVAL_SECONDS = 5  

# Start the camera preview and wait for sensor to stabilise
picam2.start()
time.sleep(2)

# The main capture loop
while True:
    # Create unique filename
    filename = time.strftime(f"{SAVE_PATH}%Y%m%d_%H%M%S.jpg")

    # Capture and save the image
    picam2.capture_file(filename)
    print(f"Captured: {filename}")

    # Wait for the next interval
    time.sleep(INTERVAL_SECONDS)
    
    
    
    
    