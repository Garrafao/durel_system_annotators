

## Section: Testing

You can run integration tests on the following datasets (running /tests/data.py will build these datasets except tempowic, you need to run evonlp2wug.sh script before running data.py) using the random, xlmr, and lexeme models:

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

There is one script to test each of the three models. Run the following commands one by one from the root directory to run tests:

1. `python ./tests/integration/test_random_annotate.py`
2. `python ./tests/integration/test_xlmr_naive_annotate.py`
3. `python ./tests/integration/test_x1_lexeme_annotate.py`

To test the LEXEME model, you need  WordTransformer.py and InputExample.py files which are found in the root directory. The requirements2.txt contains a full list of required libraries for WordTransformer, InputExample together with the annotation tool requirements.


Each of the test will also produce annotations and evaluation resutls which will be stored in the `self.custom_dir` mentioned in the test scripts above. Two result files will be produced for each test, one containing evaluation metrics and the other containing predictions. The *-labels.csv file contains predictions and *-output.csv contains evaluation scores.


**Note:** The lexeme model has not been fully tested so errors are expected. However if you are able to install and import WordTransformer successfully, it is expected to work.
