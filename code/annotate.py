import json
import logging
import random
from optparse import OptionParser

import pandas as pd

import xl_lexeme

# For new annotators:
# import NEW_ANNOTATOR_NAME

"""
This script handles the main annotation process, i.e. reading the input file, calling the specified annotator and 
writing the annotations to the output annotation file.
"""


def main(annotator, usage_dir, annotation_dir, annotation_filename, prefix, debug, thresholds, settings_location):
    """

    :param annotator: The name of the annotator to use. It should be one of the available annotators.
    :param usage_dir: The directory where the usage data is stored.
    :param annotation_dir: The directory where annotation data is stored.
    :param annotation_filename: The filename of the custom data.
    :param prefix: The prefix to use for custom data files.
    :param debug: A boolean flag indicating whether debug mode is enabled.
    :param thresholds: A dictionary containing the thresholds for the annotator.
    :param settings_location: The location of the settings file.

    This method performs the main functionality of the program. It checks the annotation input and logging, loads the
    settings file, creates an annotation provider, and generates annotations based on the chosen annotator.
    The annotations are then added to the annotation provider and saved to a file.

    Note: To add another annotator, you need to add the appropriate code within the if-elif block.

    """
    # Setup
    with open(settings_location) as settings_file:
        settings = json.load(settings_file)

    annotation_input_logging(annotator, debug, usage_dir, annotation_dir, annotation_filename, settings)

    df = load_dataframe(settings, prefix, usage_dir)

    # Get judgments
    judgments = None
    if annotator == "XL-Lexeme":
        judgments = xl_lexeme.create_annotations_for_input_data(df, settings['batch_size'],
                                                                thresholds, settings['model_dir'])
        annotator = xl_lexeme.specify_xl_lexeme_annotator(thresholds)

    elif annotator == "Random":
        judgments = random.choices([1, 4], k=len(df))

    # If you want to add another annotator, add the following here:
    # elif annotator == "NEW_ANNOTATOR_NAME":
    #       code here
    #       cls_result = some_function_in_NEW_ANNOTATOR_NAME.py()

    df = complete_the_dataframe(df, annotator, judgments, settings)

    df.to_csv(format_path(annotation_dir, prefix, annotation_filename, settings['file_extension']),
              sep=settings['delimiter'], index=False)


def load_dataframe(settings: dict, prefix: str, usage_dir: str, level: str = 'relaxed') -> pd.DataFrame:
    delimiter = settings['delimiter']
    token_index_filepath = format_path(usage_dir, prefix, settings['token_index_filename'], settings['file_extension'])
    df = pd.read_csv(token_index_filepath, header='infer', delimiter=delimiter, quoting=3, escapechar='\\')
    validate_dataframe(df, level)
    return df

def validate_dataframe(df: pd.DataFrame, level: str = 'relaxed'):
    for column1, column2 in [('context1','indexes_target_token1'), ('context2','indexes_target_token2')]:
        for context, target_indices in zip(df[column1], df[column2]):
            #print(context, target_indices)
            if level == 'strict':
                pass
            elif level == 'relaxed':
                pass
            else:
                print('No dataframe validation applied.')
                pass


def format_path(directory: str, prefix: str, filename: str, file_extension: str) -> str:
    return directory + '/{}'.format(prefix) + filename + file_extension


def complete_the_dataframe(df: pd.DataFrame, annotator: str, judgments: list, settings: dict) -> pd.DataFrame:
    """
    Complete the dataframe with given parameters.

    :param df: (pandas.DataFrame) The dataframe to be completed.
    :param annotator: (str) The annotator value to assign to the 'annotator' column.
    :param judgments: (list) The list of judgment values to assign to the 'judgment' column.
    :param settings: (dict) A dictionary of settings for completing the dataframe.

    :return: The completed dataframe.
    :rtype: (pandas.DataFrame)
    """
    # Assign specific values
    df['annotator'] = annotator
    df['comment'] = ''
    df['judgment'] = judgments
    # Add absent columns
    for col in settings['annotations_columns']:
        if col not in df.columns:
            df[col] = ''
    # Drop the unwanted columns, sort other columns
    return df[settings['annotations_columns']]


def annotation_input_logging(annotator, debug, usage_dir, annotation_dir, annotation_filename, settings):
    if debug:
        logging.basicConfig(format=settings['log_formatting'], level=logging.DEBUG)
        logging.info("Debug mode is on.")
        logging.info(f"Using annotator '{annotator}' to store annotations.")
        logging.info(f"Using directory '{usage_dir}' for usage data.")
        logging.info(f"Using directory '{annotation_dir}' to store annotations.")
        logging.info(f"Using filename '{annotation_filename}' to store annotations.")


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", "--annotator", dest="annotator", default="XL-Lexeme",
                      help="Should be XL-Lexeme or Random. Default XL-Lexeme.")

    parser.add_option("-p", "--prefix", dest="prefix", type=str, default="",
                      help="Prefix for the usage, instance and annotation files. Default empty string.")
    parser.add_option("-u", "--usage_dir", dest="usage_dir", default='./temp', type=str,
                      help="Directory containing uses and instances data. Default: './temp'.")
    parser.add_option("-c", "--annotation_dir", dest="annotation_dir", default='./temp', type=str,
                      help="Directory to store custom annotations. Default: './temp'.")
    parser.add_option("-f", "--annotation_filename", dest="annotation_filename", default="annotations.csv",
                      help="Filename to store custom annotations. Default 'annotations.csv'.")

    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Enable debug mode.")
    parser.add_option("-t", "--thresholds", dest="thresholds", type=list[int], default=None,
                      help="Thresholds for cutoff if mapping to labels is requested.")
    parser.add_option("-s", "--settings_location", default='./settings/repository-settings.json',
                      dest="settings_location", type=str, help="Default: './settings/repository-settings.json'")
    (options, args) = parser.parse_args()
    logging.info(options)

    main(options.annotator, options.usage_dir, options.annotation_dir, options.annotation_filename, options.prefix,
         options.debug, options.thresholds, options.settings_location)
