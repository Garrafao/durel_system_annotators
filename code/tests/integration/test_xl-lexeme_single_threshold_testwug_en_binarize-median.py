import sys
sys.path.append('./code')
import json

import unittest

from annotate import main as annotator_main
import os

from evaluation import *

test_data_directory_path = "./test_data/datasets/"
settings_file_location = "./settings/repository-settings.json"

with open(settings_file_location) as settings_file:
    settings = json.load(settings_file)


class TestAnAnnotator(unittest.TestCase):
    def setUp(self):
        self.lexeme_annotator = 'XL-Lexeme'  # or 'Random'
        self.usage_dir_test_en_binarize_median = test_data_directory_path + 'testwug_en_transformed_binarize-median/data/all/'


        self.usage_dir_test_wic_train = test_data_directory_path + 'WiC_dataset_transformed/train/data/all/'
        self.usage_dir_test_wic_dev = test_data_directory_path + 'WiC_dataset_transformed/dev/data/all/'
        self.usage_dir_test_wic_test = test_data_directory_path + 'WiC_dataset_transformed/test/data/all/'

        self.usage_dir_test_dwug_de = test_data_directory_path + 'dwug_de_transformed_binarize-median/data/all/'
        self.usage_dir_test_dwug_en = test_data_directory_path + 'dwug_en_transformed_binarize-median/data/all/'
        self.usage_dir_test_dwug_sv = test_data_directory_path + 'dwug_sv_transformed_binarize-median/data/all/'

        self.usage_dir_test_tempowic_train = test_data_directory_path + 'tempowic_train_all_transformed/data/all/'
        self.usage_dir_test_tempowic_trial = test_data_directory_path + 'tempowic_trial_all_transformed/data/all/'
        self.usage_dir_test_tempowic_validation = test_data_directory_path + 'tempowic_validation_all_transformed/data/all/'

        self.prefix = ''
        self.custom_dir = './temp/'
        if not os.path.exists(self.custom_dir):
            os.makedirs(self.custom_dir)
        self.custom_filename = 'annotations'
        self.custom_ending = ".csv"
        self.debug = True
        self.thresholds = [0.2]  # for multi-threshold

    # def tearDown(self):
    # remove the test files after the test is finished
    #    os.remove(self.test_file_path)
    #    os.remove(self.output_file_path)

    def test_xl_lexeme_main_test_en_binarize_median(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_en_binarize_median, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename + self.custom_ending))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_en_binarize_median, self.thresholds,dataset='testwug_en_transformed_binarize-median')


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestAnAnnotator('test_xl_lexeme_main_test_en_binarize_median'))

    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())