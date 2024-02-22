import json
import random
from optparse import OptionParser

from code.annotation_provider import AnnotationProvider
from code.xl_lexeme import *


def main(annotator, usage_dir, custom_dir, custom_filename, prefix, debug, thresholds):
    check_annotation_input_and_logging(annotator, debug, usage_dir, custom_dir, custom_filename)

    with open('./settings/repository-settings.json') as settings_file:  # to do: should this be an input argument?
        settings = json.load(settings_file)

    annotation_provider = AnnotationProvider(usage_dir, prefix, DEBUG=debug)

    cls_result = None
    if annotator == "XL-Lexeme":
        annotation_provider.flush_instance_with_token_index(path=custom_dir)
        # TODO fill in columns and delimiter
        columns = ["word", "sentence_left", "token_index_of_sentence_left",
                   "sentence_right", "token_index_of_sentence_right"]
        delimiter = "\t"
        cls_result = make_inference_for_dataset(custom_dir + '/{}'.format(prefix) + settings['token_index_filename'],
                                                delimiter, columns, thresholds)
        annotator = specify_xl_lexeme_annotator(thresholds)

    for i, instance in enumerate(annotation_provider.get_instances_iterator(RANDOM=False)):
        judgment = cls_result[i] if cls_result is not None else random.choice([*instance['label_set']])
        columns = settings['judgment_columns']
        # TODO the column structure shouldn't be hardcoded here.
        annotation_provider.add_judgement({columns[0]: instance['lemma'], columns[1]: instance['instanceID'],
                                           columns[2]: instance['internal_identifier1'], columns[3]:
                                               instance['internal_identifier2'],
                                           columns[4]: judgment, columns[5]: '-'})

    # Save the judgement
    annotation_provider.flush_judgement(path=custom_dir, filename=custom_filename, annotator=annotator)


def check_annotation_input_and_logging(annotator, debug, usage_dir, custom_dir, custom_filename):
    if debug:
        logging.info(f"Using annotator '{annotator}' to store judgements.")

    if debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info("Debug mode is on.")

    if debug:
        logging.info(f"Using directory '{usage_dir}' for usage data.")

    if custom_dir is None:
        custom_dir = usage_dir
    if debug:
        logging.info(f"Using directory '{custom_dir}' to store judgements.")

    if debug:
        logging.info(f"Using filename '{custom_filename}' to store judgements.")


def specify_xl_lexeme_annotator(thresholds: list[int]) -> str:
    if thresholds is not None and len(thresholds) == 1:
        return "XL-Lexeme-Binary"
    elif thresholds is not None and len(thresholds) == 3:
        return "XL-Lexeme-Multi-Threshold"
    else:
        return "XL-Lexeme-Cosine"


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", "--annotator", dest="annotator", default="XL-Lexeme",
                      help="Should be XL-Lexeme or Random. Default XL-Lexeme.")

    parser.add_option("-p", "--prefix", dest="prefix", type=str, default="",
                      help="Prefix for the usage, instance and judgement files. Default empty string.")
    parser.add_option("-u", "--usage_dir", dest="usage_dir", required=True,
                      help="Directory containing uses and instances data. Required.")
    parser.add_option("-c", "--judgment_dir", dest="judgment_dir", type=str,
                      help="Directory to store custom judgements. Defaults to the value given for usage_dir.")
    parser.add_option("-f", "--judgment_filename", dest="judgment_filename", default="judgements.csv",
                      help="Filename to store custom judgements. Default 'judgements.csv'.")

    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Enable debug mode.")
    parser.add_option("-t", "--thresholds", dest="thresholds", type=list[int], default=None,
                      help="Thresholds for cutoff if mapping to labels is requested.")
    parser.add_option("-s", "--sub-word", dest="sub-word", help="provide sub-word subword_aggregation.")
    (options, args) = parser.parse_args()
    logging.info(options)
    default_thresholds = [0.2, 0.4, 0.6]

    main(options.annotator, options.usage_dir, options.custom_dir, options.custom_filename, options.prefix,
         options.debug, options.thresholds)
