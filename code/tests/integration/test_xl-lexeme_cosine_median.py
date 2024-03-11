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
        #self.usage_dir_test_en_target = test_data_directory_path + 'testwug_en_transformed_binarize-median/data/all/'

        self.usage_dir_test_en_median = test_data_directory_path + 'testwug_en_transformed_median/data/all/'
        #self.usage_dir_test_en_target_median = test_data_directory_path + 'testwug_en_transformed_median/data_split/target/'


        self.usage_dir_test_wic_train = test_data_directory_path + 'WiC_dataset_transformed/train/data/all/'
        self.usage_dir_test_wic_dev = test_data_directory_path + 'WiC_dataset_transformed/dev/data/all/'
        self.usage_dir_test_wic_test = test_data_directory_path + 'WiC_dataset_transformed/test/data/all/'

        self.usage_dir_test_dwug_de = test_data_directory_path + 'dwug_de_transformed_binarize-median/data/all/'
        self.usage_dir_test_dwug_en = test_data_directory_path + 'dwug_en_transformed_binarize-median/data/all/'
        self.usage_dir_test_dwug_sv = test_data_directory_path + 'dwug_sv_transformed_binarize-median/data/all/'

        self.usage_dir_test_dwug_de_median = test_data_directory_path + 'dwug_de_transformed_median/data/all/'
        self.usage_dir_test_dwug_en_median = test_data_directory_path + 'dwug_en_transformed_median/data/all/'
        self.usage_dir_test_dwug_sv_median = test_data_directory_path + 'dwug_sv_transformed_median/data/all/'


        self.usage_dir_test_tempowic_train = test_data_directory_path + 'tempowic_train_all_transformed/data/all/'
        self.usage_dir_test_tempowic_trial = test_data_directory_path + 'tempowic_trial_all_transformed/data/all/'
        self.usage_dir_test_tempowic_validation = test_data_directory_path + 'tempowic_validation_all_transformed/data/all/'

        self.prefix = ''
        self.custom_dir = './temp/'
        if not os.path.exists(self.custom_dir):
            os.makedirs(self.custom_dir)
        self.custom_filename = 'annotations'
        self.debug = True
        self.thresholds = None


    # def tearDown(self):
    # remove the test files after the test is finished
    #    os.remove(self.test_file_path)
    #    os.remove(self.output_file_path)

    def test_xl_lexeme_main_test_en_binarize_median(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_en_binarize_median, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds, settings_file_location)

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_en_binarize_median, self.thresholds,self.debug,dataset='testwug_en_transformed_binarize-median')

    def test_xl_lexeme_main_test_en_median(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_en_median, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename + settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_en_median, self.thresholds,self.debug,dataset='testwug_en_transformed_median')



    def test_xl_lexeme_main_wic_train(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_wic_train, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_train, self.thresholds,self.debug,dataset='wic_train')

    def test_xl_lexeme_main_wic_dev(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_wic_dev, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_dev, self.thresholds,self.debug,dataset='wic_dev')

    def test_xl_lexeme_main_wic_test(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_wic_test, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_test, self.thresholds,self.debug,dataset='wic_test')

    def test_xl_lexeme_main_dwug_en(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_dwug_en, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_en, self.thresholds,self.debug,dataset='dwug_en')

    def test_xl_lexeme_main_dwug_de(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_dwug_de, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_de, self.thresholds,self.debug,dataset='dwug_de')

    def test_xl_lexeme_main_dwug_sv(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_dwug_sv, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_sv, self.thresholds,self.debug,dataset='dwug_sv')


    def test_xl_lexeme_main_dwug_en_median(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_dwug_en_median, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_en, self.thresholds,self.debug,dataset='dwug_en_median')

    def test_xl_lexeme_main_dwug_de_median(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_dwug_de_median, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_de, self.thresholds,self.debug,dataset='dwug_de_median')

    def test_xl_lexeme_main_dwug_sv_median(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_dwug_sv_median, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_sv, self.self.thresholds,self.debug,dataset='dwug_sv_median')

    def test_xl_lexeme_main_tempowic_train(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_tempowic_train, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_tempowic_train, self.thresholds,self.debug,dataset='tempowic_train')

    def test_xl_lexeme_main_tempowic_trial(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_tempowic_trial, self.custom_dir, self.custom_filename,
                       self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_tempowic_trial, self.thresholds,self.debug,dataset='tempowic_trial')

    def test_xl_lexeme_main_tempowic_validation(self):
        # call the function to be tested
        annotator_main(self.lexeme_annotator, self.usage_dir_test_tempowic_validation, self.custom_dir,
                       self.custom_filename, self.prefix, self.debug, self.thresholds,settings_file_location)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir + self.custom_filename+settings['file_extension']))

        # check that the contents of the output file are correct
        # acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_tempowic_validation, self.thresholds,dataset='tempowic_validation')


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestAnAnnotator('test_xl_lexeme_main_test_en_binarize_median'))

    test_suite.addTest(TestAnAnnotator('test_xl_lexeme_main_test_en_median'))

    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_wic_train'))
    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_wic_dev'))
    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_wic_test'))

    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_dwug_en'))
    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_dwug_de'))
    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_dwug_sv'))

    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_dwug_en_median'))
    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_dwug_de_median'))
    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_dwug_sv_median'))

    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_tempowic_train'))
    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_tempowic_trial'))
    test_suite.addTest( TestAnAnnotator('test_xl_lexeme_main_tempowic_validation'))

    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
