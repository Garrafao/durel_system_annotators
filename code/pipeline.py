import json
import logging
import os
import random
import subprocess
import torch

import requests

from status_enum import StatusEnum


def get_gpu_usage():
    torch.cuda.empty_cache()
    gpu_max_memory = torch.cuda.get_device_properties(0).total_memory
    gpu_memory_allocated = torch.cuda.memory_allocated()
    gpu_load = (gpu_memory_allocated / gpu_max_memory) * 100
    return gpu_load


def authenticate():

    url = settings['url'] + settings['auth_route']

    with requests.Session() as s:
        r = s.post(url, json={
            'username': settings['username'],
            'password': settings['password']})
        print(r.content)

    if r.status_code == 200:
        return r.json()['jwt']
    else:
        print('Error: ' + str(r.status_code))


# HELPER FUNCTIONS ########
def update_task_status(task_id, status):
    """
    Update the status of a task with the given task ID.

    Example:
    update_task_status(123, 'completed')

    :param task_id: (int): The ID of the task to update the status for.
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
    url = settings['url'] + settings['/tasks/next']
    print("url for next task: " + url)
    r = requests.get(url,
                     headers={'Authorization': auth})

    # If status code is not 200, exit
    if r.status_code != 200:
        exit(1)

    new_task = r.json()

    # If no task is available, exit
    if new_task['id'] == 0:
        exit(0)

    logging.info(new_task)
    logging.info("Annotator is: %s", task['annotatorType'])
    return new_task


def get_instances():
    """
    Retrieves instances from the server based on the provided word or project.
    """
    if word is None:
        url = settings['url'] + settings['instance_with_project_route'].format(project)
    else:
        url = settings['url'] + settings['instance_with_word_route'].format(project, word)

    print(url)
    r = requests.get(url, headers={
        'Authorization': auth
    })

    if r.status_code != 200:
        update_task_status(task['id'], StatusEnum.TASK_FAILED.value)
        exit(1)

    with open('tmp/{}instances_with_token_index.csv'.format(prefix), 'w') as f:
        f.write(r.content.decode('utf-8'))


def annotate():
    """
    This method is used to run an annotation process based on the given annotator type. It determines the annotation
    script to use based on the annotator type and executes the script using subprocess.
    The output is written to a log file.

    :return: The subprocess result object.
    """
    def determine_script():
        """
        Determine the script based on the annotator type.

        :return: str: The script path.
        """
        if annotator_type == "Random":
            return settings['randomAnnotatorScript']
        else:
            return settings['xl-lexemeAnnotatorScript']

    annotation_script_to_use = determine_script()

    with open('logs/subprocess.logs', 'w') as f:
        if annotator_type == "XL-Lexeme-Binary":
            process = subprocess.run(
                [python_env, annotation_script_to_use, '-u', 'tmp', '-p', prefix, '-o' 'label'], stdout=f,
                stderr=subprocess.PIPE)
        elif annotator_type == "XL-Lexeme-Cosine":
            process = subprocess.run(
                [python_env, annotation_script_to_use, '-u', 'tmp', '-p', prefix, '-o', 'distance'], stdout=f,
                stderr=subprocess.PIPE)
        else:
            process = subprocess.run(
                [python_env, annotation_script_to_use, '-u', 'tmp', '-p', prefix, "-d", '-a' 'Random'], stdout=f,
                stderr=subprocess.PIPE)
    return process


def finish_annotation():
    """
    Finish the annotation process.

    This method checks if the completed process has a return code of 0. If it does not,
    it updates the task status to 'TASK_FAILED'. Otherwise, it uploads the judgements to the server.
    """
    if completed_process.returncode != 0:
        update_task_status(task['id'], StatusEnum.TASK_FAILED.value)

    # JUDGEMENT UPLOAD ########
    # Upload judgements
    else:
        url = settings['url'] + settings['upload_annotation_route']
        print("url for upload votes: " + url)
        # build multipart form data for file upload with owner, project, phase and task id
        files = [("files", open('tmp/{}annotations.csv'.format(prefix), 'rb'))]

        r = requests.post(url,
                          headers={'Authorization': auth},
                          files=files,
                          data={'projectName': task["projectName"],
                                'task_id': task['id']})
        os.remove('tmp/{}judgements.csv'.format(prefix))
        print(r.text)


def delete_temporary_files():
    os.remove('tmp/{}instances.csv'.format(prefix))


# 1 - Check GPU
load = get_gpu_usage()
if load > 70:
    exit("GPU has too much load!")

# 2 - Setup
with open('settings/repository-settings.json') as settings_file:
    settings = json.load(settings_file)
logging.basicConfig(filename=settings['logFilePath'], filemode='a', format=settings['logFormatting'],
                    level=logging.INFO)

python_env = os.path.join(os.getcwd(), settings['envName'], "bin", "python")
# Get authentication token
auth = 'Bearer ' + authenticate()

# 3 - Get task
task = get_tasks()
project = task["projectName"]
word = task["word"]
annotator_type = task["annotatorType"]
prefix = str(random.randint(0, 1000))

# 4 - Annotation
logging.info("Start annotation")
completed_process = annotate()
# Capture stderr output from the completed process
stderr_output = completed_process.stderr.decode('utf-8')
if stderr_output:
    logging.error(stderr_output)

# 5 - Finish annotation
finish_annotation()
