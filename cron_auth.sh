#!/bin/bash

WORKDIR=$1
echo $WORKDIR

# Change to the working directory
cd $WORKDIR 

## Cronjob for authentication
# start the virtual environment
source random-annotator-venv/bin/activate

# run authentication
python3 authenticator.py

# deactivate the virtual environment
deactivate