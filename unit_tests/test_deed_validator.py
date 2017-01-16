import unittest

import mock

from application.deed.deed_validator import Validation
from application.deed.validate_borrowers import BorrowerNamesDifferException, BorrowerNamesMissingException


class TestDeedValidator(unittest.TestCase):

    def create_a_borrower_differ_exception(self, msg):
        raise BorrowerNamesDifferException('Test exception')

    def create_a_borrower_missing_exception(self, msg):
        raise BorrowerNamesMissingException('Test exception')

    @mock.patch('application.deed.deed_validator.compare_borrower_names')
    @mock.patch('application.deed.deed_validator.all_borrower_names_present')
    def test_validate_borrower_names_compare_fail(self, mock_present, mock_name_check):
        """
        Test that the function fails correctly if borrower and proprietor names don't match.
        """
        expected_fail_msg = "Only a person who is entered in the register as proprietor or joint proprietor " \
              "of the registered estate can be named as a borrower."

        mock_name_check.side_effect = self.create_a_borrower_differ_exception
        result, actual_msg = Validation().validate_borrower_names({})
        self.assertEqual(result, False)
        self.assertEqual(actual_msg, expected_fail_msg)

    @mock.patch('application.deed.deed_validator.compare_borrower_names')
    @mock.patch('application.deed.deed_validator.all_borrower_names_present')
    def test_validate_borrower_names_all_present_fail(self, mock_present, mock_name_check):
        """
        Test that the function fails if borrower names aren't all present.
        """
        expected_fail_msg = "Please add all borrowers names. All those entered in the register as proprietor " \
                            "or joint proprietor of the registered estate must be named as a borrower."

        mock_present.side_effect = self.create_a_borrower_missing_exception
        result, actual_msg = Validation().validate_borrower_names({})
        self.assertEqual(result, False)
        self.assertEqual(actual_msg, expected_fail_msg)

    @mock.patch('application.deed.deed_validator.compare_borrower_names')
    @mock.patch('application.deed.deed_validator.all_borrower_names_present')
    def test_validate_borrower_names_compare_success(self, mock_present, mock_name_check):
        """
        Test that the function succeeds if borrower and proprietor names match.
        """
        expected_success_msg = ""

        mock_name_check.return_value = True, ""
        result, actual_msg = Validation().validate_borrower_names({})
        self.assertEqual(result, True)
        self.assertEqual(actual_msg, expected_success_msg)
