
from optparse import OptionParser
import logging

from annotation_provider import AnnotationProvider
from inference import *

def main(usage_dir, custom_dir, custom_filename, prefix, debug):

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

    # Example annotator that randomly annotates the given set
    annotation_provider = AnnotationProvider(usage_dir, prefix, DEBUG=debug)

    annotation_provider.flush_instance_with_token_index(path=custom_dir)

    # instance_id = 34
    # annotation_provider.flush_single_instance_wic(instance_id, path=custom_dir)

    cls_result = make_inference_for_dataset('tmp/instances_with_token_index.csv')

    for i, instance in enumerate(annotation_provider.get_instances_iterator(RANDOM=True)):
        annotation_provider.add_judgement({'instanceID': instance['instanceID'], 'internal_identifier1': instance['internal_identifier1'], 'internal_identifier2': instance['internal_identifier2'], 'label': cls_result[i], 'comment': '-'})

    # print(annotation_provider._uses)
    # print(annotation_provider._instances)
    # print(annotation_provider._judgements)
    # print(annotation_provider._instances_in_wic_format)
    # Save the judgement
    annotation_provider.flush_judgement(path=custom_dir, filename=custom_filename)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--usage_dir", dest="usage_dir", help="Directory containing uses and instances data")
    parser.add_option("-p", "--prefix", dest="prefix", help="Prefix for the usage and instances files")
    parser.add_option("-c", "--custom_dir", dest="custom_dir", help="Directory to store custom judgements")
    parser.add_option("-f", "--custom_filename", dest="custom_filename", help="Filename to store custom judgements")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Enable debug mode")
    (options, args) = parser.parse_args()
    print(options)
    main(options.usage_dir, options.custom_dir, options.custom_filename, options.prefix, options.debug)

# python xlmr_naive_annotate.py -u tmp -p "" -d