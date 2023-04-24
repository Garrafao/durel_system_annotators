# Overview
This annotation pipeline is a server component runs independently of the durel application, this means this component could be deployed at a different server with respect to the durel application. Currently we are deploying it at a GPU server to increase processing speed. 

# Deployment
To deploy this component, login to the steppenweihe.ims.uni-stuttgart.de GPU server and change to directory /mount/arbeitsdaten20/projekte/cik/shared/computational_annotators, this is a space specically reserver for this component so it does not exceed storage space. Then you could clone this repository.
After cloning, go into the repo and create a python env with the command:

`python3 -m venv random-annotator-venv`

activate the env with:

`source random-annotator-venv/bin/activate`

after activating the env, install dependencies with:

`pip install -r requirements.txt`

Note you have to create the env just under the root directory of the project and with the name I have specified in the command, if you want to create the env elsewhere or change the env name, you have to change the code correspondingly in the cron_taskmng.sh and cron_auth.sh file.

Then, set the huggingface cache location with nano:

`nano ~/.bashrc`

check if the line below is already in the the .bashrc file, if not you should add this line to the .bashrc file:

`export HF_HOME=/mount/arbeitsdaten20/projekte/cik/shared/hf_cache`
`

Execute the `.bashrc`:

`source ~/.bashrc`

After the above process, first create a task in the durel web application.

next, run the command:

`python authenticator.py`

and:

`python pipeline.py`

If the two scripts above do not throw any errors, then you could start the cronjob with:

`bash cron_mng.sh`

The cronjob executes the two python scripts above with the predefined interval in the cron_mng.sh file. 

# Configuration
The cron_mng.sh is a script for cronjob, it has two subtasks, the first one is for getting validated tokens to access the api endpoints on the durel application, the second if for retreiving impending tasks from the durel database and annotate this task. You could modify the schedule of these two subtasks according to your preferance. 

# Logs
The cron_mng.sh execute two python pipelines: 

1. The first is authenticator.py, the log for this pipeline is located in the /logs/cron_auth.logs of this repo. 

2. The second is the pipeline.py, the log for this script is located in the /logs/cron_taskmng.logs of this repo. Note this script also initiates a subprocess which calls specifc annotation script (search the variable annotation_script_to_use in the pipeline.py to find where the subprocess call happens), the log for this subprocess is in logs/subprocess.logs of this repo. 

You should look at these logs for debugging purpose in case the pipeline fails or does not produce the intended result.

# Potential problems
This pipeline will load large language model, so you should make sure the server have enough space for storing the cache for huggingface. Currently, the cache is set to be stored in the /mount/arbeitsdaten20/projekte/cik/shared so this should not cause a problem. But bear in mind in case the pipeline does not work, the exceeded space could always be a cause. 

Because this server component will constantly retrive impending tasks from the durel application, this means multpile annotators could in theory run at the same time, currently there is no restriction in this regard so if too many annotators are running at the same time, this could lead to memeory overload. Decreasing the frequency of this component retriving tasks from the durel should mitigate this potential problem.

Also, we load all the sentences at one batch, it is unclear if this approach will lead to memory overuse, you might want to have more sophisticated way of loading sentences.

# Known issues
The xlmr annotator could not process data row in which the index of the word is given wrongly, this happens with the dema word in the test_uug dataset and possibly other dataset not tested yet.

# Notes 
The xlmr annotator currently concatenates two word embeddings according to their order in the instances file, which means you concatenate the word embdding of the internal_identifier2 after the word embedding of the internal_identifier1. The future code might want to explore the effect of this ordering condition.

# Performance metrics
The xlmr annotator currently achieves 60% accuracy on the dev set of the WiC dataset.

# Annotator account
We have created two annotator accounts which correspond to two automatic annotators we currently have, the username is random and xlmr+mlp+binary, the password is both admin.

# Todo
Create a capabilities so the server application could create user account on the durel server. We might want this because there is a corresponding user account with the automatic annotator, basically, the annotation result is stored in this account. Currently we manual create this user account.


