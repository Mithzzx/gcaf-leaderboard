#!/bin/bash

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/scraper.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Scraper process ID file not found. The scraper may not be running."
    exit 1
fi

# Get the PID from the file
PID=$(cat "$PID_FILE")

# Check if the process exists
if ! ps -p "$PID" > /dev/null; then
    echo "Scraper process (PID: $PID) is not running."
    rm "$PID_FILE"
    exit 1
fi

# Kill the process
echo "Stopping scraper process (PID: $PID)..."
kill "$PID"

# Wait for the process to terminate
attempt=0
while ps -p "$PID" > /dev/null && [ $attempt -lt 10 ]; do
    echo "Waiting for process to terminate..."
    sleep 1
    attempt=$((attempt + 1))
done

# Force kill if still running
if ps -p "$PID" > /dev/null; then
    echo "Process did not terminate gracefully. Forcing termination..."
    kill -9 "$PID"
fi

# Remove the PID file
rm "$PID_FILE"
echo "Scraper stopped successfully."