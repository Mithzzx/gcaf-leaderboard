import os
import subprocess
import logging
from datetime import datetime
import time

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
        start_time = time.time()
        
        # Get the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scraper_script = os.path.join(script_dir, "cloud_profile_scraper.py")
        
        # Project root is 2 levels up from script directory
        project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
        
        # Log the actual project root for debugging
        logging.info(f"Project root directory: {project_root}")
        
        # Save to data directory - this is the standard location
        data_dir = os.path.abspath(os.path.join(project_root, "data", "profiles"))
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        output_file = os.path.join(data_dir, "profiles_data.csv")
        
        # Also save to the project root for backward compatibility
        root_output_file = os.path.join(project_root, "profiles_data.csv")
        
        # Log all file paths for debugging
        logging.info(f"Script directory: {script_dir}")
        logging.info(f"Scraper script: {scraper_script}")
        logging.info(f"Output file: {output_file}")
        logging.info(f"Root output file: {root_output_file}")
        
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
            
            # Check if the output file exists and has content
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                logging.info(f"Output file exists with size: {file_size} bytes")
                
                if file_size == 0:
                    logging.warning("Output file is empty (0 bytes)")
            else:
                logging.error(f"Output file {output_file} was not created")
            
            # Copy to the project root for backward compatibility
            try:
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    with open(output_file, 'r') as src, open(root_output_file, 'w') as dst:
                        content = src.read()
                        dst.write(content)
                    logging.info(f"Data copied to {root_output_file} ({len(content)} bytes)")
                else:
                    logging.warning(f"Not copying to root because source file is missing or empty")
            except Exception as e:
                logging.error(f"Error copying data to root: {e}")
                
            # Also copy to public directory for direct serving
            public_dir = os.path.abspath(os.path.join(project_root, "public"))
            if not os.path.exists(public_dir):
                os.makedirs(public_dir)
                
            public_output_file = os.path.join(public_dir, "data.csv")
            try:
                # Copy the file to public directory
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    with open(output_file, 'r') as src, open(public_output_file, 'w') as dst:
                        content = src.read()
                        dst.write(content)
                    logging.info(f"Data copied to {public_output_file} ({len(content)} bytes)")
                else:
                    logging.warning(f"Not copying to public because source file is missing or empty")
            except Exception as e:
                logging.error(f"Error copying data to public dir: {e}")
            
            logging.debug(f"Output: {result.stdout}")
        else:
            logging.error(f"Scraper failed with return code {result.returncode}")
            logging.error(f"Error: {result.stderr}")
            # Log the actual stdout too for debugging
            logging.error(f"Output: {result.stdout}")
        
        # Calculate and log execution time
        end_time = time.time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)
        logging.info(f"Total scraping time: {int(minutes)} minutes and {int(seconds)} seconds")
            
    except Exception as e:
        logging.error(f"Error running scraper: {e}")
        import traceback
        logging.error(traceback.format_exc())

def main():
    logging.info("Running the cloud profile scraper")
    
    # Run once without scheduling
    run_scraper()
    
    logging.info("Scraper completed successfully")

if __name__ == "__main__":
    main()