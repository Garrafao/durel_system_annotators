# Overview
This annotation pipeline is a server component runs independently of the durel application, this means this component could be deployed at a different server with respect to the durel application. Currently we are deploying it at a GPU server to increase processing speed. 

# Deployment
To deploy this component, login to the steppenweihe.ims.uni-stuttgart.de GPU server and change to directory /mount/arbeitsdaten20/projekte/cik/shared/computational_annotators, this is a space specically reserver for this component so it does not exceed storage space. Then you could clone this repository.
After cloning, go into this repository and run cron_mng.sh with:

`bash cron_mng.sh`

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

# Notes 
The xlmr annotator currently concatenates two word embeddings according to their order in the instances file, which means you concatenate the word embdding of the internal_identifier2 after the word embedding of the internal_identifier1. The future code might want to explore the effect of this ordering condition.

# Performance metrics
The xlmr annotator currently achieves 60% accuracy on the dev set of the WiC dataset.

# Annotator account
We have created two annotator accounts which correspond to two automatic annotators we currently have, the username is random and xlmr+mlp+binary, the password is both admin.



