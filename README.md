# Overview
This annotation pipeline is a server component runs independently of the DURel application, this means this component could be deployed at a different server with respect to the DURel application. Currently, we are deploying it at a GPU server to increase processing speed.

# Deployment

## New Installation

To deploy this component, login to the steppenweihe.ims.uni-stuttgart.de GPU server and change to directory /mount/arbeitsdaten20/projekte/cik/shared/computational_annotators, this is a space specifically reserver for this component, so it does not exceed storage space. Then you could clone this repository.

### Python Environment
After cloning, go into the repo and create a python env with the command:

`python3 -m venv annotator-venv`

Activate the env with:

`source annotator-venv/bin/activate`

After activating the env, install dependencies with:

```
git clone git@github.com:pierluigic/xl-lexeme.git
cd xl-lexeme
pip3 install .
pip install pandas
```

Note you have to create the env just under the root directory of the project and with the name I have specified in the command, if you want to create the env elsewhere or change the env name, you have to change the code correspondingly in the cron_taskmng.sh and cron_auth.sh file.

### Language Model Locations

TODO

See Troubleshooting Language Models below.

### Annotator accounts
We have created an account that logs into the server to retrieve and upload the data. This account is called AnnotatorServer.
We also have created annotator accounts which correspond to the automatic annotators we currently have, the usernames are Random, XL-Lexeme-Binary, Xl-Lexeme-Cosine and XL-Lexeme-Multiple. The password for all accounts is `!aSfFrH"#7e7WD#`.

### Test the setup

See separate section testing below.

### Running the Pipeline

After the above process, first create a task in the DURel web application.

next, run the command:

`python authenticator.py`

and:

`python pipeline.py`

### Cronjob
The interaction with the DURel system is managed through cronjob.

If the two scripts (authenticate.py and pipeline.py) do not throw any errors, and you have tested the annotators using the integration tests, you could start the cronjob with:

`bash cron_mng.sh`

The cronjob executes the two python scripts above with the predefined interval in the cron_mng.sh file.

The cron_mng.sh is a script for cronjob, it has two subtasks, the first one is for getting validated tokens to access the api endpoints on the DURel application, the second if for retrieving impending tasks from the DURel database and annotate this task. You could modify the schedule of these two subtasks according to your preference.

## Redeployment

For redeployment, `git pull` the newest version of the repository while in the root folder.
Then run the tests (see below).

# The annotators and DURel

Some of the python scripts in this repository contain structures (uses, instances, annotations)
that have to relate to the respective output of DURel for this repository to work. We have tried to
move most hard-coded parameters to the settings file. However, there might still be problems when there
is a larger update to DURel. You should definitely check the settings and `annotation_provider.py`.

To make sure that there are no problems, you should run the `pipeline_test.py` after each redeployment of DURel.

# Models

The repository currently contains these models:

- Random: samples a random integer between 1 and 4 with uniform probability.
- XL-Lexeme-Cosine: [XL-Lexeme](https://github.com/pierluigic/xl-lexeme) is a bi-encoder that vectorizes the input sequences using a XLMR-based Siamese Network. It is trained to minimize the contrastive loss with cosine distance on several WiC datasets. XL-Lexeme-Cosine returns the cosine similarity between word vectors.
- XL-Lexeme-Multi: Predicts an integer between 1 and 4 based on thresholding cosine similarity between XL-Lexeme vectors at specified triple of thresholds (default is [0.2, 0.4, 0.6]).
- XL-Lexeme-Binary: Predicts either value 1 or 4 based on thresholding cosine similarity between XL-Lexeme vectors at specified threshold (default is 0.5).

## Adding new models

In order to add new models you should follow these steps:

1. Add a new file NEW_ANNOTATOR.py to the code subdirectory.
2. Check if there are any new packages that need to be added to the requirements.
3. Import this file into annotate.py.
4. Add a new elif block regarding the new annotator after line 50 of the annotate.py script

# Testing

1. You can run integration tests on the following datasets (running /tests/data.py will build these datasets except tempowic, you need to run evonlp2wug.sh script before running data.py) using the random and lexeme models:

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

2. There is one script to test each of the three models. Run the following commands one by one from the root directory to run tests:

    `python ./code/tests/integration/test_an_annotator.py`

    Each of the test will also produce annotations and evaluation results which will be stored in the `self.custom_dir` mentioned in the test scripts above. Two result files will be produced for each test, one containing evaluation metrics and the other containing predictions. The *-labels.csv file contains predictions and *-output.csv contains evaluation scores.

# Troubleshooting

## Known Installation Issues
- Tested installation on Python 3.10, might have some issues if you are trying with an earlier python version.
- You might get 'No space left on device' error while installing. It might be that the temp dir is full. Try creating a temp-dir in your home dir, e.g. ~/tmp and prefix whatever command you're running with TMPDIR=~/tmp. For example, TMPDIR=~/tmp pip install PACKAGE_NAME.

## Code needs update after changes to DURel

Sometimes the annotator might break after DURel updates (see Annotator and DURel above).

## Potential Problems
This pipeline will load large language models, so you should make sure the server have enough space for storing the cache for huggingface and pytorch. Currently, the cache is set to be stored in the /mount/arbeitsdaten20/projekte/cik/shared so this should not cause a problem. But bear in mind in case the pipeline does not work, the exceeded space could always be a cause.

Because this server component will constantly retrieve impending tasks from the DURel application, this means multiple annotators could in theory run at the same time, currently there is no restriction in this regard so if too many annotators are running at the same time, this could lead to memory overload. Decreasing the frequency of this component retrieving tasks from the DURel should mitigate this potential problem.

Also, we load all the sentences at one batch, it is unclear if this approach will lead to memory overuse, you might want to have more sophisticated way of loading sentences.

## Logs
The cron_mng.sh execute two python pipelines:

1. The first is authenticator.py, the log for this pipeline is located in the /logs/cron_auth.logs of this repo.

2. The second is the pipeline.py, the log for this script is located in the /logs/cron_taskmng.logs of this repo. Note this script also initiates a subprocess which calls specific annotation script (search the variable annotation_script_to_use in the pipeline.py to find where the subprocess call happens), the log for this subprocess is in logs/subprocess.logs of this repo.

You should look at these logs for debugging purpose in case the pipeline fails or does not produce the intended result.

