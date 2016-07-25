import unittest
from application.borrower.model import Borrower
import mock
from unit_tests.helper import DeedHelper
import copy


class TestBorrowerModel(unittest.TestCase):

    def test_borrower_token(self):
        token = Borrower.generate_token()
        char_list = ['I', 'O', 'W', 'Z']
        res = False

        if any((c in char_list) for c in token):
            res = True

        self.assertTrue(token.isupper())
        self.assertFalse(res)

    @mock.patch('application.borrower.model.Borrower._get_borrower_internal')
    @mock.patch('application.borrower.model.db', autospec=True)
    def test_update_borrower_by_id(self, mock_db, mock_query):

        updated_borrower = copy.deepcopy(DeedHelper._valid_single_borrower_update)

        testBorrower = Borrower()

        testBorrower.id = updated_borrower['id']
        testBorrower.token = "AAAA"
        testBorrower.deed_token = "AAAA"
        testBorrower.forename = updated_borrower['forename']
        testBorrower.middlename = updated_borrower['middle_name']
        testBorrower.surname = updated_borrower['surname']
        testBorrower.dob = updated_borrower['dob']
        testBorrower.gender = updated_borrower['gender']
        testBorrower.phonenumber = updated_borrower['phone_number']
        testBorrower.address = updated_borrower['address']
        testBorrower.esec_user_name = ""

        mock_query.return_value = testBorrower

        updated_borrower["forename"] = "Frank"

        borrower = Borrower()
        res = borrower.update_borrower_by_id(updated_borrower, "AAAA")

        self.assertEqual(res.forename, "Frank")

    @mock.patch('application.borrower.model.Borrower._get_borrower_internal')
    @mock.patch('application.borrower.model.db', autospec=True)
    def test_update_borrower_by_id_token_mismatch(self, mock_db, mock_query):

        updated_borrower = copy.deepcopy(DeedHelper._valid_single_borrower_update)

        testBorrower = Borrower()

        testBorrower.id = updated_borrower['id']
        testBorrower.token = "AAAA"
        testBorrower.deed_token = "AAAA"
        testBorrower.forename = updated_borrower['forename']
        testBorrower.middlename = updated_borrower['middle_name']
        testBorrower.surname = updated_borrower['surname']
        testBorrower.dob = updated_borrower['dob']
        testBorrower.gender = updated_borrower['gender']
        testBorrower.phonenumber = updated_borrower['phone_number']
        testBorrower.address = updated_borrower['address']
        testBorrower.esec_user_name = ""

        mock_query.return_value = testBorrower

        borrower = Borrower()
        res = borrower.update_borrower_by_id(updated_borrower, "BBBB")

        self.assertEqual(res, "Error Token Mismatch")
