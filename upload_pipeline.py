import configparser
import requests
import subprocess
from enum import Enum
import os
import numpy as np

######## ENUMS ########
class StatusEnum(Enum):
    TASK_PENDING = 'TASK_PENDING'
    TASK_STARTED = 'TASK_STARTED'
    TASK_COMPLETED = 'TASK_COMPLETED'
    TASK_FAILED = 'TASK_FAILED'

######## HELPER FUNCTIONS ########
def update_task_status(config, task_id, status):
    url = config['SERVER']['url'] + config['TASK-ROUTES']['update_status'].format(task_id, status)

    r = requests.patch(url, headers={
        'Authorization': auth
    })

    if r.status_code != 200:
        print('Error: ' + str(r.status_code))
        exit(1)

current_file_path = os.path.abspath(__file__)
print("current file path:" + current_file_path)
parent_dir_path = os.path.dirname(current_file_path)

python_env = os.path.join(parent_dir_path, "random-annotator-venv", "bin", "python")


os.makedirs(os.path.join(parent_dir_path, "tmp"), exist_ok=True)
os.makedirs(os.path.join(parent_dir_path, "logs"), exist_ok=True)
######## CONFIGURATION ########

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

# Load authentication token
auth = 'Bearer ' + config['CREDENTIALS']['authentication_token']

######## JUDGEMENT UPLOAD ########
# Upload judgements
url = config['SERVER']['url'] + config['JUDGEMENT-ROUTES']['judgement']
print("url for upload votes: " + url)
# build multipart form data for file upload with owner, project, phase and task id
# files = {'file': ('judgements.csv', open('tmp/{}judgements.csv'.format(prefix), 'rb'), 'text/tab-separated-values')} 
files = [("files", open('tmp/judgements.csv', 'rb'))]

r = requests.post(url, headers={
    'Authorization': auth
}, files=files, data={
    'projectName': PROJECTNAME, 'task_id': ID
})

print(r.text)