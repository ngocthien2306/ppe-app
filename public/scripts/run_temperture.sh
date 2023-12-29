#!/bin/bash

# Get the current username
CURRENT_USER=$(whoami)

# Activate the virtual environment directly
. /home/$CURRENT_USER/.virtualenvs/ppe/bin/activate
# Define the target directory based on the current username
TARGET_DIR="/home/$CURRENT_USER/Downloads/repos/ppe-app"

# Check if the directory exists
if [ -d "$TARGET_DIR" ]; then
    # Change to the target directory
    cd "$TARGET_DIR" || { echo "Error: Could not change to $TARGET_DIR" >&2; exit 1; }

    # Run the Python script
    python3 test/temperture.py || { echo "Error: Failed to execute temperture.py" >&2; exit 1; }
else
    echo "Error: Directory $TARGET_DIR not found." >&2
    exit 1
fi

