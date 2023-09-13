import configparser
import requests
import subprocess
from enum import Enum
import os

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

######## NEXT TASK LOAD ########
# Get next task
url = config['SERVER']['url'] + config['TASK-ROUTES']['next']
print("url for next task: " + url)
r = requests.get(url, headers={
    'Authorization': auth
})

# If status code is not 200, exit
if r.status_code != 200:
    exit(1)

# If no task is available, exit
# if r.content == b'':
#     exit(0)
task = r.json()

print(task)

if task['id'] == 0:
    print("no task to do on the durel server")
    exit(0)

######## USES ########
project = task["projectName"]
word = task["word"]
annotator_type = task["annotatorType"]
print("annotator_type is: " + annotator_type)
if (annotator_type == "Random"):
    annotation_script_to_use = "random_annotate.py"
elif (annotator_type == "XLMR+MLP+Binary"):
    annotation_script_to_use = "xlmr_naive_annotate.py"
elif (annotator_type == "XL-Lexeme" or annotator_type == "XL-Lexeme-Cosine"):
    annotation_script_to_use = "x1_lexeme_annotate.py"


if word == None:
    url = config['SERVER']['url'] + config['USAGE-ROUTES']['usage_with_project'].format(project)
else:
    url = config['SERVER']['url'] + config['USAGE-ROUTES']['usage_with_word'].format(project, word)

print(url)

r = requests.get(url, headers={
    'Authorization': auth
})

if r.status_code != 200:
    update_task_status(config, task['id'], StatusEnum.TASK_FAILED.value)
    exit(1)

with open('tmp/uses.csv', 'w') as f:
    f.write(r.content.decode('utf-8'))

######## INSTANCES ########

if word == None:
    url = config['SERVER']['url'] + config['INSTANCE-ROUTES']['instance_with_project'].format(project)
else:
    url = config['SERVER']['url'] + config['INSTANCE-ROUTES']['instance_with_word'].format(project, word)


print(url)
r = requests.get(url, headers={
    'Authorization': auth
})

if r.status_code != 200:
    update_task_status(config, task['id'], StatusEnum.TASK_FAILED.value)
    exit(1)

with open('tmp/instances.csv', 'w') as f:
    f.write(r.content.decode('utf-8'))

######## ANNOTATION ########
prefix = ""
with open('logs/subprocess.logs', 'w') as f:
    if (annotator_type == "XL-Lexeme"):
        completed_process = subprocess.run([python_env, annotation_script_to_use, '-u', 'tmp', '-p', prefix, '-f' 'judgements.csv', '-o' 'label'], stdout=f, stderr=subprocess.PIPE)
    elif (annotator_type == "XL-Lexeme-Cosine"):
        completed_process = subprocess.run([python_env, annotation_script_to_use, '-u', 'tmp', '-p', prefix, '-f', 'judgements.csv', '-o', 'distance'], stdout=f, stderr=subprocess.PIPE)
    else:
        completed_process = subprocess.run([python_env, annotation_script_to_use, '-u', 'tmp', '-p', prefix, "-d"], stdout=f, stderr=subprocess.PIPE)



# Capture stderr output from the completed process
stderr_output = completed_process.stderr.decode('utf-8')
print(stderr_output)
# Print the stderr output if there is any
if stderr_output:
    print(f"output from standard error, this could be simply from the logging message from the annotator component: {stderr_output}")

print("start annotation")

if completed_process.returncode != 0:
    update_task_status(config, task['id'], StatusEnum.TASK_FAILED.value)
    exit(1)

######## JUDGEMENT UPLOAD ########
# Upload judgements
url = config['SERVER']['url'] + config['JUDGEMENT-ROUTES']['judgement']
print("url for upload votes: " + url)
# build multipart form data for file upload with owner, project, phase and task id
# files = {'file': ('judgements.csv', open('tmp/{}judgements.csv'.format(prefix), 'rb'), 'text/tab-separated-values')} 
files = [("files", open('tmp/{}judgements.csv'.format(prefix), 'rb'))]

r = requests.post(url, headers={
    'Authorization': auth
}, files=files, data={
    'annotator': task["annotatorType"]
})

print(r.text)

if r.status_code != 200:
    update_task_status(config, task['id'], StatusEnum.TASK_FAILED.value)
    exit(1)

# Set task status to completed
update_task_status(config, task['id'], StatusEnum.TASK_COMPLETED.value)
