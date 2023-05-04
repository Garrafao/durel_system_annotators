import sys
sys.path.append('../../')
import unittest
from annotation_provider import AnnotationProvider


class TestAnnotationProvider(unittest.TestCase):
    def test_init_with_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            annotation_provider = AnnotationProvider("nonexistent_file.txt")

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestAnnotationProvider('test_init_with_nonexistent_file'))
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
