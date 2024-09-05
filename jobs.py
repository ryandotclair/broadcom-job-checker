import requests
import urllib3
import os
import logging
from logging.handlers import RotatingFileHandler

# Define the file names
new_jobs_file = '/appdata/jobs.new.txt'
jobs_file = '/appdata/jobs.txt'

# Define tokens
user_token = os.getenv("USER_TOKEN")
app_token = os.getenv("APP_TOKEN")

# Define and configure logger
log_path = '/appdata/jobs.log'
logger = logging.getLogger(__name__)
logging.basicConfig(filename='jobs.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
max_log_size = 1 * 1024 * 1024  # Limit it to 1 MB
backup_count = 3  # Keep 3 backup files
file_handler = RotatingFileHandler(log_path, maxBytes=max_log_size, backupCount=backup_count)
file_handler.setLevel(logging.DEBUG)

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the URL and headers
url = 'https://broadcom.wd1.myworkdayjobs.com/wday/cxs/broadcom/External_Career/jobs'
headers = {
    'accept': 'application/json',
    'accept-language': 'en-US',
    'content-type': 'application/json',
    'origin': 'https://broadcom.wd1.myworkdayjobs.com'
}

# Define the payload (note: locations is Plano,TX and TX remote. Also returns a max of 20, ordered from most recent to oldest)
payload = {
    "appliedFacets": {
        "locations": [
            "036f545a07811067fe3102fad18abe98",
            "0dd627624e2e013c1b0b00dadcd9d20c"
        ]
    },
    "offset": 0,
    "searchText": ""
}

# Send the POST request
response = requests.post(url, headers=headers, json=payload, verify=False)

# Check if the request was successful
if response.status_code == 200:
    job_data = response.json()
    job_paths = [job['externalPath'] for job in job_data.get('jobPostings', []) if job.get('externalPath')]
    total_jobs = job_data.get('total')
    # Save the job paths to a file
    with open(new_jobs_file, 'w') as file:
        for path in job_paths:
            file.write(f"https://broadcom.wd1.myworkdayjobs.com/External_Career{path}\n")

    if total_jobs > 20:
        offset = 20

        while total_jobs > 0:
            payload = {
                "appliedFacets": {
                    "locations": [
                        "036f545a07811067fe3102fad18abe98",
                        "0dd627624e2e013c1b0b00dadcd9d20c"
                    ]
                },
                "offset": offset,
                "searchText": ""
            }

            response = requests.post(url, headers=headers, json=payload, verify=False)

            if response.status_code == 200:
                job_data = response.json()
                job_paths = [job['externalPath'] for job in job_data.get('jobPostings', []) if job.get('externalPath')]

                # Append the new_jobs_file with the next page
                with open(new_jobs_file, 'a') as file:
                    for path in job_paths:
                        file.write(f"https://broadcom.wd1.myworkdayjobs.com/External_Career{path}\n")

                # Grab the next page
                total_jobs -= offset
                offset += 20

    logger.info("jobs.new.txt file has been updated")

    # Read the contents of the files into sets
    with open(new_jobs_file, 'r') as f:
        new_jobs = set(f.read().splitlines())

    # Check if the old jobs file exists
    if not os.path.exists(jobs_file):
        # If it doesn't exist, create it by copying the new jobs file and "initiate" this script.
        with open(jobs_file, 'w') as f:
            f.write('\n'.join(sorted(new_jobs)))
        logger.info(f"{jobs_file} did not exist, so it was created with the contents of {new_jobs_file}.")
    else:
        # If the old jobs file exists, read its contents into a set
        with open(jobs_file, 'r') as f:
            jobs = set(f.read().splitlines())

        # Check if the files match fully
        if new_jobs == jobs:
            logger.info("No new jobs!")
            # logger.info(f"Total jobs is {len(jobs)}")
        else:
            # Check for removed job listings
            removed_jobs = jobs - new_jobs
            for job in removed_jobs:
                logger.info(f"Job listing removed! {job}")
                jobs.remove(job)

            # Check for new job listings
            new_listings = new_jobs - jobs
            for job in new_listings:
                logger.warning(f"New job listing! {job}")
                # Send this to phone
                url = f"https://api.pushover.net/1/messages.json?token={app_token}&user={user_token}&url={job}&message={job}&title=BCOM%20Job%20Alert!"

                response = requests.request("POST", url, verify=False)

                logger.info(response.text)
                jobs.add(job)

            # Update the old jobs file
            with open(jobs_file, 'w') as f:
                f.write('\n'.join(sorted(jobs)))


else:
    logger.error(f"Failed to retrieve jobs. Status code: {response.status_code}")
