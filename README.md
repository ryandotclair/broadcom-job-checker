# Purpose
Checks for any new job listings, and sends a push notification to Pushover.net service

# Requirements
- Signing up for pushover.net (30 day free trial, then a one-time $5 charge for lifetime access)
- Docker

# Installation Steps
- git clone this repo
- Run `docker build -t bcom-monitor .`

# Usage
To run the script, simply run `docker run -it -e APP_TOKEN="<app_token>" -e USER_TOKEN="<user_token>" -v .:/appdata bcom-monitor` from a folder you want the two job files to be generated at (jobs.new.txt [what's latest list of jobs] and jobs.txt [list of jobs already known])

> Note: 
> - You'll need to plug in Pushover.net's app and user token. The App token is created when you register a new app. The User token is tied to your user.
> - Script looks specifically for /appdata folder in the container, and it only works when data persists across runs (read: must use -v)

Recommend running this as a cron job (hourly example: `0 * * * *`)
