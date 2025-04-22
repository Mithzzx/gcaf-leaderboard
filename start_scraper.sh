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
python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"

# Check if the scraper is already running
PID_FILE="$SCRIPT_DIR/scraper.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        echo "Scraper is already running with PID: $PID"
        exit 1
    else
        echo "Removing stale PID file..."
        rm "$PID_FILE"
    fi
fi

# Record start time
start_time=$(date +%s)

# Run the scheduler in the background
echo "Starting the profile scraper scheduler..."
cd "$SCRIPT_DIR/backend/src"
nohup python3 scheduler.py > /dev/null 2>&1 &

# Save the PID
echo $! > "$PID_FILE"
echo "Scraper started with PID: $!"
echo "To stop the scraper, run ./stop_scraper.sh"

# Calculate and display elapsed time
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
seconds=$((elapsed_time % 60))

echo "Scraper has been started. Initial data will be fetched in the background."
echo "Setup completed in ${seconds} seconds."