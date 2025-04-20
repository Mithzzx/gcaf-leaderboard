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
import shutil

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

# Get absolute paths to important directories
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'profiles')
PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'public')

# Log important paths
logger.info(f"Project root: {PROJECT_ROOT}")
logger.info(f"Data directory: {DATA_DIR}")
logger.info(f"Public directory: {PUBLIC_DIR}")

# Create directories if they don't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"Created data directory: {DATA_DIR}")

if not os.path.exists(PUBLIC_DIR):
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    logger.info(f"Created public directory: {PUBLIC_DIR}")

# Path to the profiles data CSV files
PROFILES_DATA_PATH = os.path.join(DATA_DIR, 'profiles_data.csv')
ROOT_PROFILES_DATA_PATH = os.path.join(PROJECT_ROOT, 'profiles_data.csv')
PUBLIC_DATA_PATH = os.path.join(PUBLIC_DIR, 'data.csv')

logger.info(f"Profiles data path: {PROFILES_DATA_PATH}")
logger.info(f"Root profiles data path: {ROOT_PROFILES_DATA_PATH}")
logger.info(f"Public data path: {PUBLIC_DATA_PATH}")

# The app URL - will be set from environment or default to localhost for development
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')

# Make sure APP_URL has a proper scheme (http:// or https://)
if APP_URL and not (APP_URL.startswith('http://') or APP_URL.startswith('https://')):
    # Check if it's a Render service ID
    if len(APP_URL) == 32 and all(c in '0123456789abcdef' for c in APP_URL):
        APP_URL = f"https://{APP_URL}.onrender.com"
    else:
        APP_URL = f"https://{APP_URL}"

logger.info(f"Using APP_URL: {APP_URL}")

def keep_alive():
    """Ping the health endpoint to keep the service alive"""
    try:
        response = requests.get(f"{APP_URL}/api/health")
        logger.info(f"Keep-alive ping: Status {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Keep-alive ping failed: {str(e)}")
        return False

def ensure_csv_files():
    """
    Make sure all CSV files are consistent by copying the most recent one
    to all required locations
    """
    try:
        # Determine the most recent CSV file
        files_to_check = [
            (PROFILES_DATA_PATH, os.path.exists(PROFILES_DATA_PATH) and os.path.getmtime(PROFILES_DATA_PATH) if os.path.exists(PROFILES_DATA_PATH) else 0),
            (ROOT_PROFILES_DATA_PATH, os.path.exists(ROOT_PROFILES_DATA_PATH) and os.path.getmtime(ROOT_PROFILES_DATA_PATH) if os.path.exists(ROOT_PROFILES_DATA_PATH) else 0),
            (PUBLIC_DATA_PATH, os.path.exists(PUBLIC_DATA_PATH) and os.path.getmtime(PUBLIC_DATA_PATH) if os.path.exists(PUBLIC_DATA_PATH) else 0)
        ]
        
        # Sort by modification time (most recent first)
        files_to_check.sort(key=lambda x: x[1], reverse=True)
        
        # Get the most recent file
        most_recent_file = files_to_check[0][0] if files_to_check[0][1] > 0 else None
        
        if most_recent_file:
            logger.info(f"Most recent CSV file: {most_recent_file}")
            
            # Copy to all locations
            for dest_file, _ in files_to_check:
                if dest_file != most_recent_file:
                    try:
                        shutil.copy2(most_recent_file, dest_file)
                        logger.info(f"Copied {most_recent_file} to {dest_file}")
                    except Exception as e:
                        logger.error(f"Error copying {most_recent_file} to {dest_file}: {e}")
        else:
            logger.warning("No CSV files found to synchronize")
            
    except Exception as e:
        logger.error(f"Error ensuring CSV files consistency: {e}")

def custom_run_scraper():
    """
    Custom wrapper for run_scraper that ensures CSV files are properly distributed
    after scraping
    """
    try:
        logger.info("Running custom_run_scraper wrapper")
        # Track time
        start_time = time.time()
        
        # Run the actual scraper
        run_scraper()
        
        # Calculate execution time
        execution_time = time.time() - start_time
        minutes, seconds = divmod(execution_time, 60)
        logger.info(f"Scraper completed in {int(minutes)} minutes and {int(seconds)} seconds")
        
        # Ensure all CSV files are updated
        logger.info("Ensuring all CSV files are consistent")
        ensure_csv_files()
        
        # Check if files exist and log their sizes
        files_to_check = [PROFILES_DATA_PATH, ROOT_PROFILES_DATA_PATH, PUBLIC_DATA_PATH]
        for file_path in files_to_check:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"CSV file {file_path} exists with size {file_size} bytes")
            else:
                logger.warning(f"CSV file {file_path} does not exist")
        
    except Exception as e:
        logger.error(f"Error in custom_run_scraper: {e}")
        import traceback
        logger.error(traceback.format_exc())

def run_schedule():
    """Background thread function to run the scheduler"""
    logger.info("Starting background scheduler")
    
    # Schedule the scraper to run every 10 minutes
    schedule.every(10).minutes.do(custom_run_scraper)
    
    # Schedule the keep-alive ping every 10 minutes
    schedule.every(10).minutes.do(keep_alive)
    
    # Also run immediately on startup
    logger.info("Running initial scraper job")
    custom_run_scraper()
    
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

@app.route('/', methods=['GET'])
def root():
    """Root endpoint that simply returns a welcome message"""
    return jsonify({
        "message": "GCAF Leaderboard API is running",
        "endpoints": {
            "leaderboard": "/api/leaderboard",
            "csv": "/api/csv",
            "health": "/api/health",
            "run-scraper": "/api/run-scraper (POST)",
            "sync-csv": "/api/sync-csv (POST)"
        }
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Return leaderboard data as JSON"""
    try:
        # First ensure CSV files are in sync
        ensure_csv_files()
        
        # Try to read from the primary location
        if os.path.exists(PROFILES_DATA_PATH):
            df = pd.read_csv(PROFILES_DATA_PATH)
            logger.info(f"Loaded leaderboard data from {PROFILES_DATA_PATH}")
        # Fall back to root location if primary doesn't exist
        elif os.path.exists(ROOT_PROFILES_DATA_PATH):
            df = pd.read_csv(ROOT_PROFILES_DATA_PATH)
            logger.info(f"Loaded leaderboard data from {ROOT_PROFILES_DATA_PATH}")
        # Try public location as a last resort
        elif os.path.exists(PUBLIC_DATA_PATH):
            df = pd.read_csv(PUBLIC_DATA_PATH)
            logger.info(f"Loaded leaderboard data from {PUBLIC_DATA_PATH}")
        else:
            logger.error("Leaderboard data not found in any location")
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
        # First ensure CSV files are in sync
        ensure_csv_files()
        
        if os.path.exists(PROFILES_DATA_PATH):
            return send_file(PROFILES_DATA_PATH, mimetype='text/csv')
        elif os.path.exists(ROOT_PROFILES_DATA_PATH):
            return send_file(ROOT_PROFILES_DATA_PATH, mimetype='text/csv')
        elif os.path.exists(PUBLIC_DATA_PATH):
            return send_file(PUBLIC_DATA_PATH, mimetype='text/csv')
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
        logger.info("Manual scraper run triggered via API")
        
        # Run in a separate thread to not block the response
        def run_scraper_thread():
            try:
                custom_run_scraper()
            except Exception as e:
                logger.error(f"Error in manual scraper thread: {str(e)}")
        
        thread = threading.Thread(target=run_scraper_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({"status": "Scraper started", "message": "The scraper is running in the background. Check logs for completion."}), 200
    except Exception as e:
        logger.error(f"Error triggering scraper: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync-csv', methods=['POST'])
def sync_csv_files():
    """Synchronize CSV files across all locations"""
    try:
        logger.info("CSV synchronization triggered via API")
        ensure_csv_files()
        return jsonify({"status": "success", "message": "CSV files synchronized"}), 200
    except Exception as e:
        logger.error(f"Error synchronizing CSV files: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the scheduler on the main thread before running the app
    scheduler_thread = threading.Thread(target=run_schedule)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)