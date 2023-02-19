#!/bin/bash

## Python
# create a virtual environment
python3 -m venv random-annotator-venv

# activate the virtual environment
source random-annotator-venv/bin/activate

# install the requirements
pip install -r requirements.txt

# deactivate the virtual environment
deactivate

## Directory
# temporary directory for data
mkdir -p tmp

# create directory for logs
mkdir -p logs

# create configuration file config.ini
touch config.ini

