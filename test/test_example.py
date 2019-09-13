"""
Example unit test.  For more information on testing in python, see
https://realpython.com/python-testing/.
Run tests from the basic directory with 'python -m unittest discover'.  Note that you can also run
unitests directly from PyCharm.
"""

import unittest

from skeleton import example

class TestExample(unittest.TestCase):
    """
    Test sum_list()
    """
    def test_list_int(self):
        """
        Test that it can sum a list of integers.
        """
        data = [1, 2, 3]
        result = example.sum_list(data)
        self.assertEqual(result, 6)

if __name__ == '__main__':
    unittest.main()
