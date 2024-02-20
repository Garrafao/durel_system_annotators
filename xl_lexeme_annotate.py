from optparse import OptionParser
import logging

from annotation_provider import AnnotationProvider
from lexeme import *

def main(usage_dir, custom_dir, custom_filename, prefix, debug,subword_aggregation,prediction_type,thresholds):

    if debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info("Debug mode is on.")

    if usage_dir is None:
        raise ValueError("usage_dir is None")
    if debug:
        logging.info(f"Using directory '{usage_dir}' for usage data.")

    if custom_dir is None:
        custom_dir = usage_dir
    if debug:
        logging.info(f"Using directory '{custom_dir}' to store judgements.")

    if custom_filename is None:
        custom_filename = "judgements.csv"
    if debug:
        logging.info(f"Using filename '{custom_filename}' to store judgements.")

    if prediction_type == "label":
        annotator = "XL-Lexeme-Binary"
    else:
        annotator = "XL-Lexeme-Cosine"

    # Example annotator that randomly annotates the given set
    annotation_provider = AnnotationProvider(usage_dir, prefix, DEBUG=debug)

    annotation_provider.flush_instance_with_token_index(path=custom_dir)

    cls_result = make_inference_for_dataset(custom_dir+'/{}instances_with_token_index.csv'.format(prefix),subword_aggregation,prediction_type,thresholds)

    for i, instance in enumerate(annotation_provider.get_instances_iterator(RANDOM=False)):
        #print({'instanceID': instance['instanceID'], 'internal_identifier1': instance['internal_identifier1'], 'internal_identifier2': instance['internal_identifier2'], 'label': cls_result[i], 'comment': '-'})
        annotation_provider.add_judgement({'lemma': instance['lemma'], 'instanceID': instance['instanceID'], 'identifier1': instance['internal_identifier1'], 'identifier2': instance['internal_identifier2'], 'judgment': cls_result[i], 'comment': '-'})

    # Save the judgement
    annotation_provider.flush_judgement(path=custom_dir, filename=custom_filename, annotator=annotator)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--usage_dir", dest="usage_dir", help="Directory containing uses and instances data")
    parser.add_option("-p", "--prefix", dest="prefix", help="Prefix for the usage, instance and judgement files")
    parser.add_option("-c", "--custom_dir", dest="custom_dir", help="Directory to store custom judgements")
    parser.add_option("-f", "--custom_filename", dest="custom_filename", help="Filename to store custom judgements")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Enable debug mode")
    parser.add_option("-s", "--subword", dest="subword", help="provide subword subword_aggregation")
    parser.add_option("-o", "--output", dest="output", help="output type either lable or distance")
    (options, args) = parser.parse_args()
    print(options)
    thresholds = [0.2,0.4,0.6]
    main(options.usage_dir, options.custom_dir, options.custom_filename, options.prefix, options.debug, options.subword, options.output,thresholds)

# python xlmr_naive_annotate.py -u tmp -p "" -d
