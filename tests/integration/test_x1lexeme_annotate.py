import sys
sys.path.append('.')
import unittest
from annotation_provider import AnnotationProvider
from x1_lexeme_annotate import *

import os
import urllib.request
from sklearn.metrics import accuracy_score


lang='en'
test_data_directory_path = "./tests/data/"

class TestX1LexemeAnnotate(unittest.TestCase):
    def setUp(self):
        self.usage_dir = test_data_directory_path+'testwug_'+lang+'/data/target/'
        self.prefix = ''
        self.custom_dir = './temp/'
        self.custom_filename = 'judgements.csv'
        self.debug = False


    #def tearDown(self):
        # remove the test files after the test is finished
    #    os.remove(self.test_file_path)
    #    os.remove(self.output_file_path)

    def test_x1_lexeme_main(self):
        # call the function to be tested
        main(self.usage_dir, self.custom_dir,self.custom_filename,self.prefix,self.debug)

        # check that the output file was created

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
        print(accuracy)
        self.assertTrue(accuracy>0.5)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestX1LexemeAnnotate('test_x1_lexeme_main'))
    #test_suite.addTest(TestAnnotationProvider('test_init_with_nonexistent_uses_file'))
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
