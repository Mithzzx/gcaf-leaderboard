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

# Record start time
start_time=$(date +%s)

# Run the scraper as a one-time operation
echo "Running the profile scraper..."
cd "$SCRIPT_DIR/backend/src"
python3 scheduler.py

# Calculate and display elapsed time
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
minutes=$((elapsed_time / 60))
seconds=$((elapsed_time % 60))

echo "Scraper has completed. Data has been fetched and saved."
echo "Total scraping time: ${minutes} minutes and ${seconds} seconds."