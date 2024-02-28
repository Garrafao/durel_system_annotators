import configparser
import requests
import subprocess
from code.statusEnum import StatusEnum
import os
import logging
import random
import json


# HELPER FUNCTIONS ########
def update_task_status(task_id, status):
    """
    Update the status of a task with the given task ID.

    Parameters:
    task_id (int): The ID of the task to update the status for.
    status (str): The new status of the task.

    Example:
    update_task_status(123, 'completed')
    """
    url = config['SERVER']['url'] + config['TASK-ROUTES']['update_status'].format(task_id, status)

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

    Returns:
        The next task as a JSON object.

    Exceptions:
        - If the status code of the response is not 200, the method will exit with status code 1.
        - If no task is available (task ID is 0), the method will exit with status code 0.
    """
    url = config['SERVER']['url'] + config['TASK-ROUTES']['next']
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


def get_uses():
    """
    Retrieve use information for a given project or word.
    """
    if word is None:
        url = config['SERVER']['url'] + config['USAGE-ROUTES']['usage_with_project'].format(project)
    else:
        url = config['SERVER']['url'] + config['USAGE-ROUTES']['usage_with_word'].format(project, word)

    logging.info("Request URL: %s", url)

    r = requests.get(url, headers={
        'Authorization': auth
    })

    if r.status_code != 200:
        update_task_status(task['id'], StatusEnum.TASK_FAILED.value)
        exit(1)

    with open('tmp/{}uses.csv'.format(prefix), 'w') as f:
        f.write(r.content.decode('utf-8'))


def get_instances():
    """
    Retrieves instances from the server based on the provided word or project.
    """
    if word is None:
        url = config['SERVER']['url'] + config['INSTANCE-ROUTES']['instance_with_project'].format(project)
    else:
        url = config['SERVER']['url'] + config['INSTANCE-ROUTES']['instance_with_word'].format(project, word)

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

        Returns:
            str: The script path.
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
        url = config['SERVER']['url'] + config['JUDGEMENT-ROUTES']['judgement']
        print("url for upload votes: " + url)
        # build multipart form data for file upload with owner, project, phase and task id
        files = [("files", open('tmp/{}judgements.csv'.format(prefix), 'rb'))]

        r = requests.post(url,
                          headers={'Authorization': auth},
                          files=files,
                          data={'projectName': task["projectName"],
                                'task_id': task['id']})
        os.remove('tmp/{}judgements.csv'.format(prefix))
        print(r.text)


def delete_temporary_files():
    os.remove('tmp/{}uses.csv'.format(prefix))
    os.remove('tmp/{}instances.csv'.format(prefix))
    os.remove('tmp/{}instances_with_token_index.csv'.format(prefix))


# Load settings file
with open('settings.json') as settings_file:
    settings = json.load(settings_file)

logging.basicConfig(filename=settings['logFilePath'], filemode='a', format=settings['logFormatting'],
                    level=logging.INFO)

current_file_path = os.path.abspath(__file__)
parent_dir_path = os.path.dirname(current_file_path)

python_env = os.path.join(parent_dir_path, settings['envName'], "bin", "python")

# CONFIGURATION ########

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

# Load authentication token
auth = 'Bearer ' + config['CREDENTIALS']['authentication_token']
task = get_tasks()
project = task["projectName"]
word = task["word"]
annotator_type = task["annotatorType"]
prefix = str(random.randint(0, 1000))
completed_process = annotate()
# Capture stderr output from the completed process
stderr_output = completed_process.stderr.decode('utf-8')

# Print the stderr output if there is any
if stderr_output:
    logging.error(stderr_output)

logging.info("Start annotation")

finish_annotation()
