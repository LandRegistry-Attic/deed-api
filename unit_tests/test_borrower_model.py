import unittest
from application.borrower.model import Borrower, VerifyMatch, DatabaseException, BorrowerNotFoundException
import mock
from unit_tests.helper import DeedHelper, borrower_object_helper, BorrowerModelMock
from application import app
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

        testBorrower = borrower_object_helper(updated_borrower)

        mock_query.return_value = testBorrower

        updated_borrower["forename"] = "Frank"

        borrower = Borrower()
        res = borrower.update_borrower_by_id(updated_borrower)

        self.assertEqual(res.forename, "Frank")

    @mock.patch('application.borrower.model.Borrower._get_borrower_internal')
    @mock.patch('application.borrower.model.db', autospec=True)
    def test_update_borrower_by_id_no_borrower(self, mock_db, mock_query):

        updated_borrower = copy.deepcopy(DeedHelper._valid_single_borrower_update)

        mock_query.return_value = None
        borrower = Borrower()

        res = borrower.update_borrower_by_id(updated_borrower)

        self.assertEqual(res, "Error No Borrower")


class TestVerifyModel(unittest.TestCase):
    def setUp(self):
        app.config.from_pyfile("config.py")
        self.app = app.test_client()

    @mock.patch('application.borrower.model.VerifyMatch.query', autospec=True)
    def test_remove_verify_match_not_found(self, mock_query):
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = None
        self.assertEqual(VerifyMatch.remove_verify_match(self, '1'), False)

    @mock.patch('application.borrower.model.VerifyMatch.query', autospec=True)
    @mock.patch('application.borrower.model.db.session.commit', autospec=True)
    @mock.patch('application.borrower.model.db.session.delete', autospec=True)
    def test_remove_verify_match_found(self, mock_delete, mock_commit, mock_query):
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = 'a thing'
        self.assertEqual(VerifyMatch.remove_verify_match(self, '1'), True)

    @mock.patch('application.borrower.model.VerifyMatch.query', autospec=True)
    def test_remove_verify_match_exception(self, mock_query):
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.side_effect = Exception('oh no')
        with self.assertRaises(DatabaseException) as context_manager:
            VerifyMatch.remove_verify_match(self, '1')
        self.assertIn('oh no', str(context_manager.exception))

    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.borrower.views.Borrower.get_by_token')
    def test_update_borrower_signing_in_progress(self, mock_borrower, mock_borrower_save):
        class ReturnedBorrower:
            id = 0000000
            token = "aaaaaa"
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            phonenumber = "07777777777"
            signing_in_progress = False

        mock_borrower.return_value = None
        mock_borrower_save.signing_in_progress = False
        with self.assertRaises(BorrowerNotFoundException):
            Borrower.update_borrower_signing_in_progress('bbbbbb')

        mock_borrower.return_value = BorrowerModelMock()
        mock_borrower.return_value.signing_in_progress = True
        self.assertEqual(Borrower.update_borrower_signing_in_progress('aaaaaa'), True)
