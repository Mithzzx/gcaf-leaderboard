import os
import subprocess
import logging
from datetime import datetime

# Set up logging
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "scraper_log.txt")),
        logging.StreamHandler()
    ]
)

def run_scraper():
    """Run the cloud profile scraper script once"""
    try:
        logging.info("Starting cloud profile scraper...")
        
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scraper_script = os.path.join(script_dir, "cloud_profile_scraper.py")
        
        # Project root is 2 levels up from script directory
        project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
        
        # Save to data directory - this is the standard location
        data_dir = os.path.abspath(os.path.join(project_root, "data", "profiles"))
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        output_file = os.path.join(data_dir, "profiles_data.csv")
        
        # Also save to the project root for backward compatibility
        root_output_file = os.path.join(project_root, "profiles_data.csv")
        
        # Run the scraper script
        python_cmd = "python3" if os.name != "nt" else "python"
        result = subprocess.run(
            [python_cmd, scraper_script, "--output", output_file],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logging.info(f"Scraper completed successfully. Data saved to {output_file}")
            
            # Copy to the project root for backward compatibility
            try:
                with open(output_file, 'r') as src, open(root_output_file, 'w') as dst:
                    dst.write(src.read())
                logging.info(f"Data also copied to {root_output_file}")
            except Exception as e:
                logging.error(f"Error copying data to root: {e}")
                
            # Also copy to public directory for direct serving
            public_dir = os.path.abspath(os.path.join(project_root, "public"))
            if not os.path.exists(public_dir):
                os.makedirs(public_dir)
                
            public_output_file = os.path.join(public_dir, "data.csv")
            try:
                # Copy the file to public directory
                with open(output_file, 'r') as src, open(public_output_file, 'w') as dst:
                    dst.write(src.read())
                logging.info(f"Data also copied to {public_output_file}")
            except Exception as e:
                logging.error(f"Error copying data to public dir: {e}")
            
            logging.debug(f"Output: {result.stdout}")
        else:
            logging.error(f"Scraper failed with return code {result.returncode}")
            logging.error(f"Error: {result.stderr}")
            
    except Exception as e:
        logging.error(f"Error running scraper: {e}")

def main():
    logging.info("Running the cloud profile scraper")
    
    # Run once without scheduling
    run_scraper()
    
    logging.info("Scraper completed successfully")

if __name__ == "__main__":
    main()