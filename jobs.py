import requests
import json
import os

# Define the file names
new_jobs_file = '/appdata/jobs.new.txt'
jobs_file = '/appdata/jobs.txt'

# Define tokens
user_token = os.getenv("USER_TOKEN")
app_token = os.getenv("APP_TOKEN")

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

    # Save the job paths to a file
    with open(new_jobs_file, 'w') as file:
        for path in job_paths:
            file.write(f"https://broadcom.wd1.myworkdayjobs.com/External_Career{path}\n")

    print("jobs.new.txt file has been updated")

    # Read the contents of the files into sets
    with open(new_jobs_file, 'r') as f:
        new_jobs = set(f.read().splitlines())

    # Check if the old jobs file exists
    if not os.path.exists(jobs_file):
        # If it doesn't exist, create it by copying the new jobs file and "initiate" this script.
        with open(jobs_file, 'w') as f:
            f.write('\n'.join(sorted(new_jobs)))
        print(f"{jobs_file} did not exist, so it was created with the contents of {new_jobs_file}.")
    else:
        # If the old jobs file exists, read its contents into a set
        with open(jobs_file, 'r') as f:
            jobs = set(f.read().splitlines())

        # Check if the files match fully
        if new_jobs == jobs:
            print("No new jobs!")
            print(f"Total jobs is {len(jobs)}")
        else:
            # Check for removed job listings
            removed_jobs = jobs - new_jobs
            for job in removed_jobs:
                print(f"Job listing removed! {job}")
                jobs.remove(job)

            # Check for new job listings
            new_listings = new_jobs - jobs
            for job in new_listings:
                print(f"New job listing! {job}")
                # Send this to phone
                url = f"https://api.pushover.net/1/messages.json?token={app_token}&user={user_token}&url={job}&message=Job%20alert!"

                response = requests.request("POST", url, verify=False)

                print(response.text)
                jobs.add(job)

            # Update the old jobs file
            with open(jobs_file, 'w') as f:
                f.write('\n'.join(sorted(jobs)))


else:
    print(f"Failed to retrieve jobs. Status code: {response.status_code}")
