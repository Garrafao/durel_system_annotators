
import unittest
from test_base import *

class CustomTestAnAnnotator(TestAnAnnotator):
    def setUp(self):
        super().setUp()  # Call parent's setUp method first
        # Override thresholds for this test class
        self.thresholds = [0.4, 0.6, 0.8] # Custom thresholds
        self.lexeme_annotator = 'XL-DURel'


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(CustomTestAnAnnotator('test_xl_durel_main_test_en_median'))

    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_wic_train'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_wic_dev'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_wic_test'))

    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_dwug_en_median'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_dwug_de_median'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_dwug_sv_median'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_tempowic_train'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_tempowic_trial'))
    test_suite.addTest( CustomTestAnAnnotator('test_xl_durel_main_tempowic_validation'))
    
    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
