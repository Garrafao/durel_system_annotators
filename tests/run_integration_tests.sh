#!/bin/bash

DIRECTORY_PATH="./tests/data"

URL="https://zenodo.org/record/7900960/files/testwug_en.zip"

# Check if the directory exists, if not create it

if [ ! -d "$DIRECTORY_PATH" ]; then
    mkdir -p "$DIRECTORY_PATH"
fi

# disable this downloading part as the data is not available at the above URL in the right format yet, Dominik will work on it
# Check if the file exists, if not download it
#FILE_PATH="$DIRECTORY_PATH/data.zip"
#if [ ! -f "$FILE_PATH" ]; then
#    wget -O "$FILE_PATH" "$URL"
#fi

#if [ -f "$FILE_PATH" ]; then
#    unzip -o "$FILE_PATH" -d "$DIRECTORY_PATH"
#fi


# run tests
#python ./tests/integration/test_random_annotate.py
python ./tests/integration/test_xlmr_naive_annotate.py
#python ./tests/integration/test_x1lexeme_annotate.py
