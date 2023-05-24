import sys
sys.path.append('.')
import unittest
from annotation_provider import AnnotationProvider
from xlmr_naive_annotate import *

import os
import urllib.request
from sklearn.metrics import accuracy_score
from scipy.stats import spearmanr

test_data_directory_path = "./tests/tests/datasets/"

class TestXLMRNaiveAnnotate(unittest.TestCase):
    def setUp(self):

        self.usage_dir_test_en = test_data_directory_path+'testwug_en_transformed/data/target/'

        self.usage_dir_test_wic_train = test_data_directory_path+'WiC_dataset_wug_transformed/train/data/all/'
        self.usage_dir_test_wic_dev = test_data_directory_path+'WiC_dataset_wug_transformed/dev/data/all/'
        self.usage_dir_test_wic_test = test_data_directory_path+'WiC_dataset_wug_transformed/test/data/all/'
        self.prefix = ''
        self.custom_dir = './temp/'
        self.custom_filename = 'judgements.csv'
        self.debug = True


    #def tearDown(self):
        # remove the test files after the test is finished
    #    os.remove(self.test_file_path)
    #    os.remove(self.output_file_path)

    def test_xlmr_main_test_en(self):
        # call the function to be tested
        main(self.usage_dir_test_en, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_en)

    def test_xlmr_main_wic_train(self):
        # call the function to be tested
        main(self.usage_dir_test_wic_train, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_train,dataset='wic')

    def test_xlmr_main_wic_dev(self):
        # call the function to be tested
        main(self.usage_dir_test_wic_dev, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_dev,dataset='wic')

    def test_xlmr_main_wic_test(self):
        # call the function to be tested
        main(self.usage_dir_test_wic_test, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        # check that the output file was created

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        acc,corr,pvalue = evaluate(self.custom_dir,self.custom_filename,self.usage_dir_test_wic_test,dataset='wic')



def evaluate(custom_dir,custom_filename,usage_dir,dataset=None):
        with open(custom_dir+custom_filename, 'r') as f:
            df = pd.read_csv(f,sep='\t')
            if dataset == 'wic':
                #print('we are in wic')
                df.loc[df['label'] == 1, 'label'] = 'F'
                df.loc[df['label'] == 4, 'label'] = 'T'
            #zip(df['internal_identifier1'],df['internal_identifier2'],df['label'])

            df_sorted = df.sort_values(['internal_identifier1','internal_identifier2'])
            #print(df_sorted)
            predicted_values = df_sorted['label']
            #print(df_sorted)
        with open(usage_dir+'judgments.csv','r') as f:
            df = pd.read_csv(f,sep='\t')
            df_sorted = df.sort_values(['internal_identifier1','internal_identifier2'])
            #print(df_sorted)
            gold_values = df_sorted['judgment']
            #print(df_sorted)
        assert len(predicted_values)==len(gold_values)
        #print(predicted_values,gold_values)

        accuracy = accuracy_score(gold_values, predicted_values)
        #print(predicted_values)
        print('Acc:',accuracy)
        #self.assertTrue(accuracy>0.5)
        correlation, p_value = spearmanr(gold_values, predicted_values)
        print('Corr:',correlation,'P-Value:',p_value)
        return (accuracy,correlation,p_value)




def suite():
    test_suite = unittest.TestSuite()
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_test_en'))
    test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_wic_train'))
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_wic_dev'))
    #test_suite.addTest(TestXLMRNaiveAnnotate('test_xlmr_main_wic_test'))
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
