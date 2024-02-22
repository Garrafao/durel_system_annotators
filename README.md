# Overview
This annotation pipeline is a server component runs independently of the durel application, this means this component could be deployed at a different server with respect to the durel application. Currently we are deploying it at a GPU server to increase processing speed.

# Deployment

## Installation

To deploy this component, login to the steppenweihe.ims.uni-stuttgart.de GPU server and change to directory /mount/arbeitsdaten20/projekte/cik/shared/computational_annotators, this is a space specically reserver for this component so it does not exceed storage space. Then you could clone this repository.

#### Python Environment
After cloning, go into the repo and create a python env with the command:

`python3 -m venv random-annotator-venv`

activate the env with:

`source random-annotator-venv/bin/activate`

after activating the env, install dependencies with:

`pip install -r requirements.txt`

Also install the second requirements file:

`pip install -r requirements2.txt`

Note you have to create the env just under the root directory of the project and with the name I have specified in the command, if you want to create the env elsewhere or change the env name, you have to change the code correspondingly in the cron_taskmng.sh and cron_auth.sh file.

#### Language Model Locations

Then, set the huggingface and pytorch cache location with nano:

`nano ~/.bashrc`

check if the line below is already in the the .bashrc file, if not you should add this line to the .bashrc file:

`export HF_HOME=/mount/arbeitsdaten20/projekte/cik/shared/hf_cache`

`export TORCH_HOME=/mount/arbeitsdaten20/projekte/cik/shared/pytorch_cache`

Execute the `.bashrc`:

`source ~/.bashrc`

#### Annotator accounts
We have created an account that logs into the server to retrieve and upload the data. This account is called AnnotatorServer.
We also have created annotator accounts which correspond to the automatic annotators we currently have, the usernames are Random, XL-Lexeme-Binary, Xl-Lexeme-Cosine and XLMR+MLP+Binary. The password for all accounts is !aSfFrH"#7e7WD#.

#### Running the Pipeline

After the above process, first create a task in the durel web application.

next, run the command:

`python authenticator.py`

and:

`python pipeline.py`

## Testing
Please find integration tests under the folder `tests/`. Some tests rely on the data created by the script `tests/data.py`. Please run the script from the main directory, if you're missing any data with

`python tests/data.py`

Also have a look at README2.md.

# Cronjobs
The interaction with the DURel system is managed through cronjobs.

If the two scripts (authenticate.py and pipeline.py) do not throw any errors, and you have tested the annotators using the integration tests, you could start the cronjob with:

`bash cron_mng.sh`

The cronjob executes the two python scripts above with the predefined interval in the cron_mng.sh file.

## Configuration
The cron_mng.sh is a script for cronjob, it has two subtasks, the first one is for getting validated tokens to access the api endpoints on the durel application, the second if for retreiving impending tasks from the durel database and annotate this task. You could modify the schedule of these two subtasks according to your preferance.

## Logs
The cron_mng.sh execute two python pipelines:

1. The first is authenticator.py, the log for this pipeline is located in the /logs/cron_auth.logs of this repo.

2. The second is the pipeline.py, the log for this script is located in the /logs/cron_taskmng.logs of this repo. Note this script also initiates a subprocess which calls specifc annotation script (search the variable annotation_script_to_use in the pipeline.py to find where the subprocess call happens), the log for this subprocess is in logs/subprocess.logs of this repo.

You should look at these logs for debugging purpose in case the pipeline fails or does not produce the intended result.

# Section: Testing

You can run integration tests on the following datasets (running /tests/data.py will build these datasets except tempowic, you need to run evonlp2wug.sh script before running data.py) using the random, xlmr, and lexeme models:

- testwug_en_arm
- testwug_en_target
- wic_test
- wic_dev
- wic_train
- dwug_de
- dwug_en
- dwug_sv
- tempowic_train
- tempowic_trial
- tempowic_validation

There is one script to test each of the three models. Run the following commands one by one from the root directory to run tests:

1. `python ./tests/integration/test_random_annotate.py`
2. `python ./tests/integration/test_xlmr_naive_annotate.py`
3. `python ./tests/integration/test_xl_lexeme_annotate.py`
python ./code/tests/integration/test_an_annotator.py

To test the LEXEME model, you need  WordTransformer.py and InputExample.py files which are found in the root directory. The requirements2.txt contains a full list of required libraries for WordTransformer, InputExample together with the annotation tool requirements.


Each of the test will also produce annotations and evaluation resutls which will be stored in the `self.custom_dir` mentioned in the test scripts above. Two result files will be produced for each test, one containing evaluation metrics and the other containing predictions. The *-labels.csv file contains predictions and *-output.csv contains evaluation scores.


**Note:** The lexeme model has not been fully tested so errors are expected. However if you are able to install and import WordTransformer successfully, it is expected to work.


# Troubleshooting

## Installation Known Issues
- Tested installation on Python 3.10, might have some issues if you are trying with an earlier python version.
- You might get 'No space left on device' error while installing. It might be that the temp dir is full. Try creating a temp-dir in your home dir, e.g. ~/tmp and prefix whatever command you're running with TMPDIR=~/tmp. For example, TMPDIR=~/tmp pip install somethingsomething.

## Potential Problems
This pipeline will load large language models, so you should make sure the server have enough space for storing the cache for huggingface and pytorch. Currently, the cache is set to be stored in the /mount/arbeitsdaten20/projekte/cik/shared so this should not cause a problem. But bear in mind in case the pipeline does not work, the exceeded space could always be a cause.

Because this server component will constantly retrive impending tasks from the durel application, this means multpile annotators could in theory run at the same time, currently there is no restriction in this regard so if too many annotators are running at the same time, this could lead to memeory overload. Decreasing the frequency of this component retriving tasks from the durel should mitigate this potential problem.

Also, we load all the sentences at one batch, it is unclear if this approach will lead to memory overuse, you might want to have more sophisticated way of loading sentences.
