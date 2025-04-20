from flask import Flask, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import sys
from pathlib import Path
import threading
import time
import schedule
import logging
import requests

# Set up logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
# Create logs directory if it doesn't exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'scraper_log.txt')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('gcaf-leaderboard')

# Add the project root directory to the path to import scraper module
sys.path.append(str(Path(__file__).parent))
try:
    from scripts.cloud_profile_scraper import scrape_cloud_profile, calculate_points, calculate_milestone
    from scripts.scheduler import run_scraper
except ImportError:
    logger.error("Failed to import scraper modules. Check file paths and module structure.")
    # Import placeholders for development
    def run_scraper():
        logger.warning("Using placeholder run_scraper function")
        return

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path to the profiles data CSV file
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'profiles')
# Create data directory if it doesn't exist
if not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)

PROFILES_DATA_PATH = os.path.join(data_dir, 'profiles_data.csv')
ROOT_PROFILES_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'profiles_data.csv')

# The app URL - will be set from environment or default to localhost for development
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')

def keep_alive():
    """Ping the health endpoint to keep the service alive"""
    try:
        response = requests.get(f"{APP_URL}/api/health")
        logger.info(f"Keep-alive ping: Status {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Keep-alive ping failed: {str(e)}")
        return False

def run_schedule():
    """Background thread function to run the scheduler"""
    logger.info("Starting background scheduler")
    
    # Schedule the scraper to run every hour
    schedule.every(1).hours.do(run_scraper)
    
    # Schedule the keep-alive ping every 10 minutes
    schedule.every(10).minutes.do(keep_alive)
    
    # Also run immediately on startup
    run_scraper()
    
    # Initial keep-alive ping
    logger.info("Performing initial keep-alive ping")
    keep_alive_success = keep_alive()
    logger.info(f"Initial keep-alive ping {'successful' if keep_alive_success else 'failed'}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Start the background scheduler in a separate thread
scheduler_thread = None

# Replace the before_first_request decorator (removed in Flask 2.0+)
# with an alternative approach that works in newer Flask versions
def start_scheduler():
    """Start the scheduler when the app starts serving requests"""
    global scheduler_thread
    if scheduler_thread is None:
        logger.info("Initializing background scheduler thread")
        scheduler_thread = threading.Thread(target=run_schedule)
        scheduler_thread.daemon = True  # Thread will exit when the main process exits
        scheduler_thread.start()
        logger.info("Background scheduler thread started")

# Register with Flask to start on first request
@app.before_request
def before_request():
    start_scheduler()
    # Remove the function after it runs once
    app.before_request_funcs[None].remove(before_request)

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Return leaderboard data as JSON"""
    try:
        # Try to read from the primary location
        if os.path.exists(PROFILES_DATA_PATH):
            df = pd.read_csv(PROFILES_DATA_PATH)
        # Fall back to root location if primary doesn't exist
        elif os.path.exists(ROOT_PROFILES_DATA_PATH):
            df = pd.read_csv(ROOT_PROFILES_DATA_PATH)
        else:
            return jsonify({"error": "Leaderboard data not found"}), 404
        
        # Convert DataFrame to list of dictionaries
        leaderboard_data = df.to_dict(orient='records')
        return jsonify(leaderboard_data)
    except Exception as e:
        logger.error(f"Error retrieving leaderboard data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/csv', methods=['GET'])
def get_csv():
    """Return the raw CSV file"""
    try:
        if os.path.exists(PROFILES_DATA_PATH):
            return send_file(PROFILES_DATA_PATH, mimetype='text/csv')
        elif os.path.exists(ROOT_PROFILES_DATA_PATH):
            return send_file(ROOT_PROFILES_DATA_PATH, mimetype='text/csv')
        else:
            return jsonify({"error": "CSV file not found"}), 404
    except Exception as e:
        logger.error(f"Error serving CSV file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/run-scraper', methods=['POST'])
def trigger_scraper():
    """Manually trigger the scraper (protected in production)"""
    try:
        # In production, you might want to add authentication here
        thread = threading.Thread(target=run_scraper)
        thread.daemon = True
        thread.start()
        return jsonify({"status": "Scraper started"}), 200
    except Exception as e:
        logger.error(f"Error triggering scraper: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the scheduler on the main thread before running the app
    scheduler_thread = threading.Thread(target=run_schedule)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)