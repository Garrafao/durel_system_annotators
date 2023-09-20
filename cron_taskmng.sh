#!/bin/sh

WORKDIR=$1
export HF_HOME=/mount/arbeitsdaten20/projekte/cik/shared/hf_cache

# Change to the working directory
cd $WORKDIR 

echo $WORKDIR
# Cronjob for getting tasks and annotating them
# start the virtual environment
source random-annotator-venv/bin/activate

# run the task manager
python3 pipeline.py &>> logs/subprocess_stderr.logs

# deactivate the virtual environment
deactivate
