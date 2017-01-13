import unittest

import mock

from application.deed.deed_validator import Validation
from application.deed.validate_borrowers import BorrowerNamesException


class TestDeedValidator(unittest.TestCase):

    def create_a_borrower_exception(self, msg):
        raise BorrowerNamesException('Test exception')

    @mock.patch('application.deed.deed_validator.check_borrower_names')
    def test_validate_borrower_names_fail(self, mock_name_check):

        expected_fail_msg = "Only a person who is entered in the register as proprietor or joint proprietor " \
              "of the registered estate can be named as a borrower."

        mock_name_check.side_effect = self.create_a_borrower_exception
        result, actual_msg = Validation().validate_borrower_names({})
        self.assertEqual(result, False)
        self.assertEqual(actual_msg, expected_fail_msg)

    @mock.patch('application.deed.deed_validator.check_borrower_names')
    def test_validate_borrower_names_success(self, mock_name_check):

        expected_success_msg = ""

        mock_name_check.return_value = True, ""
        result, actual_msg = Validation().validate_borrower_names({})
        self.assertEqual(result, True)
        self.assertEqual(actual_msg, expected_success_msg)


