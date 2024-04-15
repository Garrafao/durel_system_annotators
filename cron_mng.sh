#!/bin/sh

WORKDIR=$1

# Change to the working directory
cd $WORKDIR 

echo $WORKDIR
# Cronjob for getting tasks and annotating them
# start the virtual environment
source annotator-venv/bin/activate

# run the task manager
python3 code/pipeline.py
echo "Done"

# deactivate the virtual environment
deactivate