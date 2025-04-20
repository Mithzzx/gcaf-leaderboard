#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install required packages
echo "Installing required Python packages..."
python3 -m pip install -r "$SCRIPT_DIR/backend/requirements.txt"

# Run the scraper as a one-time operation
echo "Running the profile scraper..."
cd "$SCRIPT_DIR/backend/src"
python3 scheduler.py

echo "Scraper has completed. Data has been fetched and saved."