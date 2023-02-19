#!/bin/sh

WORKDIR=$1

# Change to the working directory
cd $WORKDIR 

# Cronjob for getting tasks and annotating them
# start the virtual environment
source .venv/bin/activate

# run the task manager
python3 taskmanager.py

# deactivate the virtual environment
deactivate