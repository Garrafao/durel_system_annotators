
import unittest
from test_base import *

class CustomTestAnAnnotator(TestAnAnnotator):
    def setUp(self):
        super().setUp()  # Call parent's setUp method first
        # Override thresholds for this test class
        self.thresholds = [0.5]  # Custom thresholds
        self.lexeme_annotator = 'XL-DURel'


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(CustomTestAnAnnotator('test_xl_durel_main_test_en_binarize_median'))

    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
