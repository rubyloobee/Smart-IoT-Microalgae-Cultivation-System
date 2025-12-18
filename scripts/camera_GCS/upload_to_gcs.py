import os
from google.cloud import storage
import config

# --- Global Initialization ---
storage_client = None
try:
    # 1. Authenticate using the JSON key file
    storage_client = storage.Client.from_service_account_json(config.CREDENTIALS_FILE)
    print("Google Cloud Storage client initialized successfully.")
except Exception as e:
    print(f"Error initializing GCS client. Cloud uploads will fail: {e}")


def upload_file_to_gcs(local_filepath):
    """ Uploads a file to the GCS bucket, makes it public, and returns the public URL."""
    if not storage_client:
        return False, None
    
    if not os.path.exists(local_filepath):
        print(f"Error: Local file not found at: {local_filepath}")
        return False, None

    # Use the filename as the object name (blob name) in GCS
    # Discard directory information and set unique name for blob when storing image in GCS
    destination_blob_name = os.path.basename(local_filepath)
    
    try:
        # Get the target bucket
        bucket = storage_client.bucket(config.BUCKET_NAME)
        
        # Create a new blob (object) reference
        blob = bucket.blob(destination_blob_name)

        # 2. Upload the file from the local path
        blob.upload_from_filename(local_filepath)
        
        # 3. Make the uploaded image publicly readable (required for Flutter/web display)
        # Bucket permission must be configured for Fine-grained access.
        blob.make_public()

        public_url = blob.public_url
        
        print(f"-> GCS Upload Success: {public_url}")
        return True, public_url

    except Exception as e:
        print(f"? Error uploading {destination_blob_name} to GCS: {e}")
        return False, None