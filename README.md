# Overview
This annotation pipeline is a server component runs independently of the DURel application, this means this component could be deployed at a different server with respect to the DURel application. Currently, we are deploying it at a GPU server to increase processing speed.

# Deployment

Check the IMS Deployment notes for more info on deploying to the server.

### Python Environment
After cloning, go into the repo and create a python env with the command:

`python3 -m venv annotator-venv`

Activate the env with:

`source annotator-venv/bin/activate`

Depending on how much space you have on your device, you might have to manually set the pip cache:

`export PIP_CACHE_DIR=/some/directory`

After activating the env, install dependencies with:

```
git clone git@github.com:pierluigic/xl-lexeme.git
cd xl-lexeme
pip3 install .
pip install pandas
pip install spacy
python -m spacy download en_core_web_sm
```

Note you have to create the env just under the root directory of the project and with the name I have specified in the command, if you want to create the env elsewhere or change the env name, you have to change the code correspondingly in the cron_taskmng.sh and cron_auth.sh file.

### Language Model Locations
This language model location is determined by a parameter in the settings file.

See Troubleshooting Language Models below.

### Test the setup

See separate section testing below.

### Combining the Annotators with DURel

After setting up DURel, make sure that there are annotator accounts for all annotators (Random, XL-Lexeme-Binary, Xl-Lexeme-Cosine and XL-Lexeme-Multi-Threshold), as well as the account `AnnotatorManagement`. Annotator accounts have the role `CANNOTATOR`. Add the login information of `AnnotatorManagement` to the settings file. Also check all other settings and adapt them if necessary.

Then create a task in the DURel web application, activate the environment, and run the command:

`python code/pipeline.py`

### Cronjob
The regular interaction with the DURel system is managed through cronjob.

If pipeline.py does not throw any errors, and you have tested the annotators using the integration tests, you could start the cronjob with:

`crontab -l | { cat; echo "bash * * * * * $(pwd)/cron_mng.sh $(pwd) >> $(pwd)/logs/cron_mng.logs 2&>1"; } | crontab -`

The cronjob executes the pipeline with the interval predefined in the `cron_mng.sh` file.

To remove a cronjob, run `crontab -e`, and edit the crontab.

### Redeployment

For redeployment, `git pull` the newest version of the repository while in the root folder. Make sure that all paths and passwords in the settings file are correct.
Then run the tests (see below).

Some of the python scripts in this repository contain structures (uses, instances, annotations)
that have to relate to the respective output of DURel for this repository to work. We have tried to
move most hard-coded parameters to the settings file. However, there might still be problems when there
is a larger update to DURel. You should definitely check the settings.

To make sure that there are no problems, you should run the `pipeline.py` manually after each redeployment of DURel.

# Models

The repository currently contains these models:

- Random: samples a random integer between 1 and 4 with uniform probability.
- XL-Lexeme-Cosine: [XL-Lexeme](https://github.com/pierluigic/xl-lexeme) is a bi-encoder that vectorizes the input sequences using a XLMR-based Siamese Network. It is trained to minimize the contrastive loss with cosine distance on several WiC datasets. XL-Lexeme-Cosine returns the cosine similarity between word vectors.
- XL-Lexeme-Multi-Threshold: Predicts an integer between 1 and 4 based on thresholding cosine similarity between XL-Lexeme vectors at specified triple of thresholds (default is [0.2, 0.4, 0.6]).
- XL-Lexeme-Binary: Predicts either value 1 or 4 based on thresholding cosine similarity between XL-Lexeme vectors at specified threshold (default is 0.5).

### Running the models

The models can be run using the `annotate.py` script. 

```
    python annotate.py --annotator <annotator> --prefix <prefix> --usage_dir <usage_directory> --annotation_dir <annotation_directory> --annotation_filename <annotation_filename> --debug --thresholds <thresholds> --settings_location <settings_location>
   ```

For more information see the README in the code folder.

### Adding new models

In order to add new models you should follow these steps:

1. Add a new file NEW_ANNOTATOR.py to the code subdirectory.
2. Check if there are any new packages that need to be added to the requirements.
3. Import the new file into annotate.py.
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

2. There is one script to test each of the three models. Each of the test will also produce annotations and evaluation results which will be stored in the `self.custom_dir` mentioned in the test scripts above. Two result files will be produced for each test, one containing evaluation metrics and the other containing predictions. The *-labels.csv file contains predictions and *-output.csv contains evaluation scores.

# Troubleshooting

## Known Installation Issues
- Tested installation on Python 3.10 and 3.11, might have some issues if you are trying with an earlier python version.
- You might get 'No space left on device' error while installing. It might be that the temp dir is full. Try creating a temp-dir in your home dir, e.g. ~/tmp and prefix whatever command you're running with TMPDIR=~/tmp. For example, TMPDIR=~/tmp pip install PACKAGE_NAME.

## Code needs update after changes to DURel

Sometimes the annotator might break after DURel updates (see Annotator and DURel above).

## Potential Problems
This pipeline will load large language models, so you should make sure the server have enough space for storing the cache for huggingface and pytorch.

Because this server component will constantly retrieve impending tasks from the DURel application, this means multiple annotators could in theory run at the same time, currently there is no restriction in this regard so if too many annotators are running at the same time, this could lead to memory overload. Decreasing the frequency of this component retrieving tasks from the DURel should mitigate this potential problem.

Also, we load all the sentences at one batch, it is unclear if this approach will lead to memory overuse, you might want to have more sophisticated way of loading sentences.

## Logs
You can check the logs of `pipeline.py` in the logs directory. Note this script also initiates a subprocess which calls specific annotation script (search the variable annotation_script_to_use in the pipeline.py to find where the subprocess call happens), the log for this subprocess is in logs/subprocess.logs of this repo.

You should look at these logs for debugging purpose in case the pipeline fails or does not produce the intended result.

