# Subprocessing
import subprocess

# HTTP requests
import requests

# Config parser
import configparser

# Other
from enum import Enum

######## ENUMS ########
class StatusEnum(Enum):
    TASK_PENDING = 'TASK_PENDING'
    TASK_STARTED = 'TASK_STARTED'
    TASK_COMPLETED = 'TASK_COMPLETED'
    TASK_FAILED = 'TASK_FAILED'

######## HELPER FUNCTIONS ########
def update_task_status(config, task_id, status):
    url = config['SERVER']['url'] + config['SERVER']['api_version'] + config['TASK-ROUTES']['update_status'].format(task_id, status)

    r = requests.post(url, headers={
        'Authorization': auth
    })

    if r.status_code != 200:
        print('Error: ' + str(r.status_code))
        exit(1)

def clean_tmp(prefix):
    import os
    if os.path.exists('tmp/{}uses.tsv'.format(prefix)):
        os.remove('tmp/{}uses.tsv'.format(prefix))
    if os.path.exists('tmp/{}instances.tsv'.format(prefix)):
        os.remove('tmp/{}instances.tsv'.format(prefix))
    if os.path.exists('tmp/{}judgements.tsv'.format(prefix)):
        os.remove('tmp/{}judgements.tsv'.format(prefix))


######## CONFIGURATION ########

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

# Load authentication token
auth = 'Bearer ' + config['CREDENTIALS']['authentication_token']


######## NEXT TASK LOAD ########
# Get next task
url = config['SERVER']['url'] + config['SERVER']['api_version'] + config['TASK-ROUTES']['next']

r = requests.get(url, headers={
    'Authorization': auth
})

# If status code is not 200, exit
if r.status_code != 200:
    exit(1)

# If no task is available, exit
if r.content == b'':
    exit(0)

task = r.json()
update_task_status(config, task['id'], StatusEnum.TASK_STARTED.value)

######## DATA LOAD ########

prefix = str(task['id']) + '-' + task['owner'] + '-' + task['project'] + '-' + task['phase'] + '-'

######## USES ########
url = config['SERVER']['url'] + config['SERVER']['api_version'] + config['USAGE-ROUTES']['usage'].format(task['owner'], task['project'])

r = requests.get(url, headers={
    'Authorization': auth
})

# If status code is not 200, set task status to failed, clean tmp and exit
if r.status_code != 200:
    update_task_status(config, task['id'], StatusEnum.TASK_FAILED.value)
    clean_tmp(prefix)
    exit(1)

# write content of usage tsv to file
with open('tmp/{}uses.csv'.format(prefix), 'w') as f:
    f.write(r.content.decode('utf-8'))


######## INSTANCES ########
url = config['SERVER']['url'] + config['SERVER']['api_version'] + config['INSTANCE-ROUTES']['instance'].format(task['owner'], task['project'], task['phase'])

r = requests.get(url, headers={
    'Authorization': auth
})

if r.status_code != 200:
    update_task_status(config, task['id'], StatusEnum.TASK_FAILED.value)
    clean_tmp(prefix)
    exit(1)

# write content of instances tsv to file
with open('tmp/{}instances.tsv'.format(prefix), 'w') as f:
    f.write(r.content.decode('utf-8'))


######## ANNOTATION ########
# TODO: somehow generalize this
completed_process = subprocess.run(['python3', config['SCRIPT']['annotator'], '-u', 'tmp', '-p', prefix])

if completed_process.returncode != 0:
    update_task_status(config, task['id'], StatusEnum.TASK_FAILED.value)
    clean_tmp(prefix)
    exit(1)


######## JUDGEMENT UPLOAD ########
# Upload judgements
url = config['SERVER']['url'] + config['SERVER']['api_version'] + config['JUDGEMENT-ROUTES']['judgement'].format(task['owner'], task['project'], task['phase'])

# build multipart form data for file upload with owner, project, phase and task id
files = {'file': ('judgements.tsv', open('tmp/{}judgements.tsv'.format(prefix), 'rb'), 'text/tab-separated-values')} 

r = requests.post(url, headers={
    'Authorization': auth
}, files=files)

if r.status_code != 200:
    update_task_status(config, task['id'], StatusEnum.TASK_FAILED.value)
    clean_tmp(prefix)
    exit(1)

# Set task status to completed
update_task_status(config, task['id'], StatusEnum.TASK_COMPLETED.value)
clean_tmp(prefix)
