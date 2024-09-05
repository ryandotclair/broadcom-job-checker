# Purpose
Checks for any new job listings, and sends a push notification to your phone via Pushover.net service

# Requirements
- Signing up for [pushover.net](https://pushover.net) (30 day free trial, then a one-time $5 charge for lifetime access)
- Docker

# Installation Steps
- Register an "app" with pushover.net (you'll need that token, as well as your pushover.net user token)
- git clone this repo
- Run `docker build -t bcom-monitor .`
- Note: If docker run fails with an error about "PermissionError: [Errno 1] Operation not permitted", which happened on my rasberry pi4, to get past it I downgraded libseccomp library. Steps:
   - Run `wget http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1~bpo10+1_armhf.deb` 
   - Run `sudo apt install ./libseccomp2_2.5.1-1~bpo10+1_armhf.deb`

# Usage
To run the script, simply run `docker run -it -e APP_TOKEN="<app_token>" -e USER_TOKEN="<user_token>" -v .:/appdata bcom-monitor` from a folder you want the various job files to be generated at

> Note: 
> - You'll need to plug in Pushover.net's app and user token. The App token is created when you register a new app. The User token is tied to your user account.
> - Script looks specifically for /appdata folder in the container, and it only works when data persists across runs (read: must use -v)
> - I've included a jobs.sh file that you can point contab to (example of it running every hour on a pi4: `0 * * * * /bin/bash /home/pi/jobs/jobs.sh`)... be sure to update the tokens and the path you want the files to live in.

# Behavior
- 3 Files get generated from this script:
  - `jobs.txt` holds the "last run" and is used to compare against the newest job grab
  - `jobs.new.txt` hold the latest job listing. If there's a job in this file that's not in the jobs.txt file, then that job's URL gets pushed to your phone
  - `jobs.log` stores all the logs, and should automatically get pruned if it exceeds 1MB
- By default this checks for two specific locations (Plano, TX and Remote-TX). This can be configured by looking at the URL once you've set your filters appropriately and modifying `jobs.py` lines 44 and 45. (ex: https://broadcom.wd1.myworkdayjobs.com/External_Career?locations=036f545a07811067fe3102fad18abe98&locations=0dd627624e2e013c1b0b00dadcd9d20c). 
