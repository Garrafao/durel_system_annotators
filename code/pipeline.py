import concurrent.futures
import json
import logging
import os
import random
import subprocess
from datetime import datetime

import torch

import requests

from status_enum import StatusEnum


def get_gpu_usage():
    torch.cuda.empty_cache()
    gpu_max_memory = torch.cuda.get_device_properties(0).total_memory
    gpu_memory_allocated = torch.cuda.memory_allocated()
    gpu_load = (gpu_memory_allocated / gpu_max_memory) * 100
    return gpu_load


def create_file(path):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    with open(path, 'a'):
        pass


def authenticate():
    login_url = settings['url'] + settings['login_route']
    auth_url = settings['url'] + settings['auth_route']

    with requests.Session() as s:
        s.post(login_url, data={
            'username': settings['username'],
            'password': settings['password']})
        r = s.post(auth_url, json={
            'username': settings['username'],
            'password': settings['password']})
        print(r.content)

    if r.status_code == 200:
        return r.json()['jwt']
    else:
        print('Error: ' + str(r.status_code))
        exit()


def update_task_status(status):
    """
    Update the status of a task with the given task ID.

    Example:
    update_task_status(123, 'completed')

    :param status: (str): The new status of the task.
    """
    url = settings['url'] + settings['update_status_route'].format(task_id, status)

    r = requests.patch(url,
                       headers={'Authorization': auth})

    if r.status_code != 200:
        print('Error: ' + str(r.status_code))
        exit(1)


def get_tasks():
    """
    Retrieve the next task from the server.

    This method sends a GET request to the server to retrieve the next task.
    It concatenates the server's URL with the 'next' route specified in the configuration file.

    :returns: The next task as a JSON object.

    Exceptions:
        - If the status code of the response is not 200, the method will exit with status code 1.
        - If no task is available (task ID is 0), the method will exit with status code 0.
    """
    url = settings['url'] + settings['next_task_route']
    r = requests.get(url,
                     headers={'Authorization': auth})

    # If status code is not 200, exit
    if r.status_code != 200:
        exit(1)
    new_task = r.json()

    logging.info(datetime.now())
    logging.info(new_task)
    logging.info("Annotator is: %s", new_task['annotatorType'])
    return new_task


def get_instances():
    """
    Retrieves instances from the server based on the provided word or project.
    """
    url = settings['url'] + settings['instance_route'].format(task_id)

    print(url)
    r = requests.get(url, headers={
        'Authorization': auth
    })

    if r.status_code != 200:
        logging.info("Failed to load file.")
        update_task_status(StatusEnum.TASK_FAILED.value)
        exit(1)

    new_prefixes = []
    content = r.content.decode('utf-8')
    for batch in content[1:-2].split('\n, '):
        prefix = str(random.randint(0, 1000))
        file_path = './temp' + '/{}'.format(prefix) + settings['token_index_filename'] + settings['file_extension']
        create_file(file_path)
        with open(file_path, 'w') as f:
            f.write(batch)
        new_prefixes.append(prefix)
    return new_prefixes


def perform_annotation(prefix):
    """
    Performs annotation for the given prefix.

    :param prefix: The prefix to be used for annotation.
    :type prefix: str
    """
    logging.info("Start annotation for prefix: " + prefix)
    completed_process = annotate(prefix)
    stderr_output = completed_process.stderr.decode('utf-8')
    if stderr_output:
        logging.error(stderr_output)
    finish_annotation(prefix, completed_process)
    delete_temporary_files(prefix)


def annotate(prefix):
    """
    This method is used to run an annotation process based on the given annotator type. It determines the annotation
    script to use based on the annotator type and executes the script using subprocess.
    The output is written to a log file.

    :return: The subprocess result object.
    """
    with open('logs/subprocess.logs', 'w') as f:
        if annotator_type == "XL-Lexeme":
            process = subprocess.run(
                [python_env, 'code/annotate.py', '-a' 'XL-Lexeme', '-p', prefix, '-t', thresholds], stdout=f,
                stderr=subprocess.PIPE)
        else:
            process = subprocess.run(
                [python_env, 'code/annotate.py', '-p', prefix], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
    return process


def finish_annotation(prefix, completed_process):
    """
    Finish the annotation process.

    This method checks if the completed process has a return code of 0. If it does not,
    it updates the task status to 'TASK_FAILED'. Otherwise, it uploads the judgements to the server.
    """
    if completed_process.returncode != 0:
        update_task_status(StatusEnum.TASK_FAILED.value)

    # JUDGEMENT UPLOAD ########
    # Upload judgements
    else:
        url = settings['url'] + settings['upload_annotation_route']
        # build multipart form data for file upload with owner, project, phase and task id
        files = [("files", open('temp/{}annotations.csv'.format(prefix), 'rb'))]

        r = requests.post(url,
                          headers={'Authorization': auth},
                          files=files,
                          data={'projectName': task["projectName"],
                                'task_id': task['id']})
        os.remove('temp/{}annotations.csv'.format(prefix))
        logging.info(r.text)


def delete_temporary_files(prefix):
    os.remove('temp/{}instances.csv'.format(prefix))


# 1 - Check GPU
if torch.cuda.is_available():
    load = get_gpu_usage()
    if load > 70:
        exit("GPU has too much load!")

# 2 - Setup
with open('settings/repository-settings.json') as settings_file:
    settings = json.load(settings_file)
create_file(settings['logFilePath'])
logging.basicConfig(filename=settings['logFilePath'], filemode='a', format=settings['log_formatting'],
                    level=logging.INFO)

python_env = os.path.join(os.getcwd(), settings['envName'], "bin", "python")
# Get authentication token
auth = 'Bearer ' + authenticate()

# 3 - Get task
task = get_tasks()
task_id = task["id"]
project = task["projectName"]
word = task["word"]
annotator_type = task["annotatorType"]
thresholds = [float(threshold) for threshold in task["thresholdValues"].split(',')] if task["thresholdValues"] else None
logging.info("Thresholds: {}".format(thresholds))

# 4 - Get instances
prefixes = get_instances()

# 5 - Annotation
# Using ProcessPoolExecutor to handle parallel tasks
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(perform_annotation, prefixes)

logging.info("Finished")
