import sys
sys.path.append('.')
#sys.path.append('./tests/')
from evaluation import *
import unittest
#from annotation_provider import AnnotationProvider
from xlmr_naive_annotate import main as xlmr_main
import numpy as np
import os
import urllib.request
from sklearn.metrics import accuracy_score
from scipy.stats import spearmanr



test_data_directory_path = "./tests/datasets/"

class TestXLMRNaiveAnnotate(unittest.TestCase):
    def setUp(self):
        self.model = 'xlmr-naive'
        self.usage_dir_test_en_target = test_data_directory_path+'testwug_en_transformed/data_split/target/'
        self.usage_dir_test_en_arm = test_data_directory_path+'testwug_en_transformed/data_split/arm/'

        self.usage_dir_test_wic_train = test_data_directory_path+'WiC_dataset_transformed/train/data/all/'
        self.usage_dir_test_wic_dev = test_data_directory_path+'WiC_dataset_transformed/dev/data/all/'
        self.usage_dir_test_wic_test = test_data_directory_path+'WiC_dataset_transformed/test/data/all/'

        self.usage_dir_test_dwug_de = test_data_directory_path+'dwug_de_transformed/data/all/'
        self.usage_dir_test_dwug_en = test_data_directory_path+'dwug_en_transformed/data/all/'
        self.usage_dir_test_dwug_sv = test_data_directory_path+'dwug_sv_transformed/data/all/'

        self.usage_dir_test_tempowic_train = test_data_directory_path+'TempoWic/tempowic_train_all_transformed/data/all/'
        self.usage_dir_test_tempowic_trial = test_data_directory_path+'TempoWic/tempowic_trial_all_transformed/data/all/'
        self.usage_dir_test_tempowic_validation = test_data_directory_path+'TempoWic/tempowic_validation_all_transformed/data/all/'

        self.prefix = ''
        self.custom_dir = './temp3/'
        if not os.path.exists(self.custom_dir):
            os.makedirs(self.custom_dir)
        self.custom_filename = 'judgements.csv'
        self.debug = True

        self.subword_aggregation = 'average' # not implemented yet
        self.prediction_type = 'label' # or it could be 'distance' or 'label'


    #def tearDown(self):
        # remove the test files after the test is finished
    #    os.remove(self.test_file_path)
    #    os.remove(self.output_file_path)

    def test_xlmr_main_test_en_target(self):
        # call the function to be tested
        xlmr_main(self.usage_dir_test_en_target, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_en_target,self.prediction_type,self.model,dataset='testwug_en_target')

    def test_xlmr_main_test_en_arm(self):
        # call the function to be tested
        xlmr_main(self.usage_dir_test_en_arm, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_en_arm,self.prediction_type,self.model,dataset='testwug_en_arm')


    def test_xlmr_main_wic_train(self):
        # call the function to be tested
        xlmr_main(self.usage_dir_test_wic_train, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_train,self.prediction_type,self.model,dataset='wic_train')

    def test_xlmr_main_wic_dev(self):
        # call the function to be tested
        xlmr_main(self.usage_dir_test_wic_dev, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_dev,self.prediction_type,self.model,dataset='wic_dev')

    def test_xlmr_main_wic_test(self):
        # call the function to be tested
        xlmr_main(self.usage_dir_test_wic_test, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_test,self.prediction_type,self.model,dataset='wic_test')


    def test_xlmr_main_dwug_en(self):
            # call the function to be tested
            xlmr_main(self.usage_dir_test_dwug_en, self.custom_dir,self.custom_filename,self.prefix,self.debug)
            # check that the output file was created

            self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

            # check that the contents of the output file are correct
            acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_en,self.prediction_type,self.model,dataset='dwug_en')

    def test_xlmr_main_dwug_de(self):
            # call the function to be tested
            xlmr_main(self.usage_dir_test_dwug_de, self.custom_dir,self.custom_filename,self.prefix,self.debug)
            # check that the output file was created

            self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

            # check that the contents of the output file are correct
            acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_de,self.prediction_type,self.model,dataset='dwug_de')

    def test_xlmr_main_dwug_sv(self):
            # call the function to be tested
            xlmr_main(self.usage_dir_test_dwug_sv, self.custom_dir,self.custom_filename,self.prefix,self.debug)
            # check that the output file was created

            self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

            # check that the contents of the output file are correct
            acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_dwug_sv,self.prediction_type,self.model,dataset='dwug_sv')

    def test_xlmr_main_tempowic_train(self):
            # call the function to be tested
            xlmr_main(self.usage_dir_test_tempowic_train, self.custom_dir,self.custom_filename,self.prefix,self.debug)
            # check that the output file was created

            self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

            # check that the contents of the output file are correct
            acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_tempowic_train,self.prediction_type,self.model,dataset='tempowic_train')

    def test_xlmr_main_tempowic_trial(self):
            # call the function to be tested
            xlmr_main(self.usage_dir_test_tempowic_trial, self.custom_dir,self.custom_filename,self.prefix,self.debug)
            # check that the output file was created

            self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

            # check that the contents of the output file are correct
            acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_tempowic_trial,self.prediction_type,self.model,dataset='tempowic_trial')

    def test_xlmr_main_tempowic_validation(self):
            # call the function to be tested
            xlmr_main(self.usage_dir_test_tempowic_validation, self.custom_dir,self.custom_filename,self.prefix,self.debug)
            # check that the output file was created

            self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

            # check that the contents of the output file are correct
            acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_tempowic_validation,self.prediction_type,self.model,dataset='tempowic_validation')



def suite():
    test_suite = unittest.TestSuite()
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_test_en_arm'))
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_test_en_target'))

    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_wic_train'))
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_wic_dev'))
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_wic_test'))

    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_dwug_de'))
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_dwug_en'))
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_dwug_sv'))

    test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_tempowic_train'))
    test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_tempowic_trial'))
    test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_tempowic_validation'))

    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
