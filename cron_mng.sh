#!/bin/sh

WORKDIR=$1

# Change to the working directory
cd $WORKDIR 

echo $WORKDIR

# Start the virtual environment with the correct path
source ~/venvs/annotator-venv/bin/activate

# Run the task manager
python3 code/pipeline.py
echo "Done"

# Deactivate the virtual environment
deactivate
