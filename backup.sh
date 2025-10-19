#!/bin/bash

# --- Configuration ---
REPO_DIR="/home/pi/pi-backup"
GIT_BRANCH="main" # Use 'master' if you initialized the old way

# --- Core Logic ---

# 1. Navigate to the repository
cd "$REPO_DIR"

# 2. Re-copy the latest versions of configuration files (Requires sudo)
# This step ensures the local repo files are up-to-date with the running system.
sudo cp /etc/dhcpcd.conf configs/
sudo cp /etc/hostname configs/
sudo cp /boot/config.txt configs/

# 3. User files (Does not required sudo)
cp /MQTT_Test/Pi_Publisher.py scripts/
cp /MQTT_Test/Pi_Subscriber.py scripts/
cp /MQTT_Bidirectional/bidirectional_main.py scripts/
cp /MQTT_Bidirectional/config.py scripts/
cp /MQTT_Bidirectional/publisher.py scripts/
cp /MQTT_Bidirectional/subscriber.py scripts/
# 4. Add all changes (configs and scripts) to the staging area
git add .

# 4. Check if there are any changes staged to prevent empty commits
if ! git diff-index --quiet --cached HEAD --; then
    # Commit with a timestamped message
    COMMIT_MESSAGE="Auto-backup: $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MESSAGE"
    
    # 5. Push changes to the remote GitHub repository
    # IMPORTANT: GitHub will require authentication here.
    # You must have either SSH keys set up or use a Personal Access Token (PAT)
    # in the URL format (https://TOKEN@github.com/...).
    git push origin "$GIT_BRANCH"
    
    echo "Backup completed: $COMMIT_MESSAGE"
else
    echo "No changes detected. Skipping push."
fi
