# download all final reports from ATS website
# final reports have a name like https://documents.ats.aq/ATCM45/fr/ATCM45_fr001_e.pdf

import os
import requests
import time
import logging

# set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# where to save PDFs
raw_data_dir = os.environ.get("DATA_RAW")
if not raw_data_dir:
    raise ValueError("DATA_RAW environment variable is not set")
out_dir = os.path.join(raw_data_dir, "fr_pdfs")

# create output directory if it doesn't exist
os.makedirs(out_dir, exist_ok=True)

# ATCMs are numbered from 1 to 45
max_atcm_nbr = 45

# for nbr in range(1, max_atcm_nbr + 1):
for nbr in range(3, max_atcm_nbr + 1):
    # construct URL and file path
    url = f"https://documents.ats.aq/ATCM{nbr}/fr/ATCM{nbr}_fr001_e.pdf"
    fname = f"ATCM{nbr}_fr001_e.pdf"
    fpath = os.path.join(out_dir, fname)
    
    # Download file
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        with open(fpath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logging.info(f"Successfully downloaded {fname}")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {fname}: {e}")
        continue
    
    # Wait 20 seconds as per robots.txt, except after the last file
    if nbr < max_atcm_nbr:
        logging.info("Waiting 20 seconds before next download...")
        time.sleep(20)

logging.info("Download process completed.")
