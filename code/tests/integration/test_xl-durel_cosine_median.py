
import unittest
from test_base import *

class CustomTestAnAnnotator(TestAnAnnotator):
    def setUp(self):
        super().setUp()  # Call parent's setUp method first
        self.lexeme_annotator = 'XL-DURel'


def suite():
    test_suite = unittest.TestSuite()


    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_dwug_en_median'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_dwug_de_median'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_dwug_sv_median'))

    '''
    test_suite.addTest(CustomTestAnAnnotator('test_xl_durel_main_test_en_binarize_median'))
    '''

    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
