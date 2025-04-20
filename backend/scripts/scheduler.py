import os
import subprocess
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_log.txt"),
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
        
        # Save to data directory
        root_dir = os.path.abspath(os.path.join(script_dir, "../.."))
        data_dir = os.path.abspath(os.path.join(root_dir, "data"))
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        output_file = os.path.join(data_dir, "profiles_data.csv")
        
        # Run the scraper script
        result = subprocess.run(
            ["python", scraper_script, "--output", output_file],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logging.info(f"Scraper completed successfully. Data saved to {output_file}")
            
            # Also copy to frontend public directory for deployment
            frontend_public_dir = os.path.abspath(os.path.join(root_dir, "public"))
            if not os.path.exists(frontend_public_dir):
                os.makedirs(frontend_public_dir)
                
            public_output_file = os.path.join(frontend_public_dir, "profiles_data.csv")
            try:
                # Copy the file to public directory
                with open(output_file, 'r') as src, open(public_output_file, 'w') as dst:
                    dst.write(src.read())
                logging.info(f"Data also copied to {public_output_file}")
            except Exception as e:
                logging.error(f"Error copying data: {e}")
            
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