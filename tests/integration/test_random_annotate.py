import sys
sys.path.append('.')
import unittest
from annotation_provider import AnnotationProvider
from random_annotate import *
import os
import urllib.request
from sklearn.metrics import accuracy_score
from scipy.stats import spearmanr
import pandas as pd
lang='en'

#test_data_directory_path = "./tests/data/"
test_data_directory_path = "./tests/tests/datasets/"

class TestRandomAnnotate(unittest.TestCase):
    def setUp(self):
        #self.usage_dir = test_data_directory_path+'testwug_'+lang+'/data/target/'
        self.usage_dir = test_data_directory_path+'testwug_'+lang+'_transformed/data/target/'
        self.prefix = ''
        self.custom_dir = './temp/'
        self.custom_filename = 'judgements.csv'
        self.debug = False
        #self.usage_dir = '/home/shafqat/changeiskey/data/WUGs/testwug_en/data/target/'
        #self.prefix = ''
        #self.custom_dir = '/home/shafqat/changeiskey/durel_system_annotators/temp/'
        #self.custom_filename = 'judgements.csv'
        #self.debug = False


    #def tearDown(self):
        # remove the test files after the test is finished
    #    os.remove(self.test_file_path)
    #    os.remove(self.output_file_path)

    def test_main(self):
        # call the function to be tested
        main(self.usage_dir, self.custom_dir,self.custom_filename,self.prefix,self.debug)
        #usage_dir, custom_dir, custom_filename, prefix, debug

        self.assertTrue(os.path.exists(self.custom_dir+self.custom_filename))

        # check that the contents of the output file are correct
        with open(self.custom_dir+self.custom_filename, 'r') as f:
            df = pd.read_csv(f,sep='\t')
            predicted_values = df['label'].values
        with open(self.usage_dir+'judgments.csv','r') as f:
            df = pd.read_csv(f,sep='\t')
            gold_values = df['judgment'].values
        assert len(predicted_values)==len(gold_values)
        #print(predicted_values,gold_values)

        accuracy = accuracy_score(gold_values, predicted_values)
        print(predicted_values)
        print('accu:',accuracy)
        #self.assertTrue(accuracy>0.5)
        correlation, p_value = spearmanr(gold_values, predicted_values)
        print('correlation:',correlation,"p_value:",p_value)

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestRandomAnnotate('test_main'))
    #test_suite.addTest(TestAnnotationProvider('test_init_with_nonexistent_uses_file'))
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
