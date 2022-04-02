"""Client unit-tests"""

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, process_response_ans


class TestClass(unittest.TestCase):
    """
    Class with tests
    """

    def test_def_presense(self):
        """Valid request test"""
        test = create_presence()
        test[TIME] = 1.1  # time must be equated otherwise the test will never pass
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_ans(self):
        """Response parsing test 200"""
        self.assertEqual(process_response_ans({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        """Correct parsing test 400"""
        self.assertEqual(process_response_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Exception test without RESPONSE field"""
        self.assertRaises(ValueError, process_response_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
