import sys
sys.path.append('.')
import unittest
from annotation_provider import AnnotationProvider
from random_annotate import *

lang='en'
test_data_directory_path = "./tests/data/"
if lang== 'en':
    url = "https://zenodo.org/record/7900960/files/testwug_en.zip"

class TestRandomAnnotate(unittest.TestCase):
    def setUp(self):
        self.usage_dir = test_data_directory_path+'testwug_'+lang+'/data/target/'
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

        # check that the output file was created
        #self.assertTrue(os.path.exists(self.usage_dir))

        # check that the contents of the output file are correct
        #with open(self.custom_dir+'/judgements.csv', 'r') as f:
        #    output_data = f.read()
        #self.assertEqual(output_data, '6\n15\n24\n')

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestRandomAnnotate('test_main'))
    #test_suite.addTest(TestAnnotationProvider('test_init_with_nonexistent_uses_file'))
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
