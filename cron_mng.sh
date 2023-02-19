### Configuration
## Authentication
# add cron_auth.sh to crontab for authentication with 3h interval
crontab -l | { cat; echo "0 */3 * * * $(pwd)/cron_auth.sh $(pwd) > $(pwd)/logs/cron_auth.logs"; } | crontab -
# run authentication once
./cron_auth.sh

## Task Management
# add cron_taskmng.sh to crontab for task management with 1min interval
crontab -l | { cat; echo "*/1 * * * * $(pwd)/cron_taskmng.sh $(pwd) > $(pwd)/logs/cron_taskmng.logs"; } | crontab -
