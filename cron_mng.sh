### Configuration
## Authentication

crontab -l | { cat; echo "0 0 * * 0 $(pwd)/cron_auth.sh $(pwd) >> $(pwd)/logs/cron_auth.logs 2&>1"; } | crontab -

# run authentication once
# ./cron_auth.sh

## Task Management
# add cron_taskmng.sh to crontab for task management with x min interval
crontab -l | { cat; echo "*/1 * * * * $(pwd)/cron_taskmng.sh $(pwd) >> $(pwd)/logs/cron_taskmng.logs 2&>1"; } | crontab -
