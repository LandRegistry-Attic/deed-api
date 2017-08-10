import unittest
import mock
from application.borrower.views import delete_verify_match, check_borrower_signing_in_progress, update_borrower_signing_in_progress


class TestBorrowerViews(unittest.TestCase):

    @mock.patch('application.borrower.views.VerifyMatch.remove_verify_match', autospec=True)
    @mock.patch('application.borrower.views.jsonify')
    @mock.patch('application.borrower.views.application.app.logger.error')
    @mock.patch('application.borrower.views.application.app.logger.debug')
    def test_delete_verify_match_false(self, mock_logger_debug, mock_logger_error, mock_jsonify, mock_verify_match):
        mock_jsonify.return_value = 'no match found for PID 200abc123: nothing removed'
        mock_verify_match.return_value = False
        self.assertEqual(delete_verify_match('200abc123'), ('no match found for PID 200abc123: nothing removed', 200))
        mock_logger_debug.assert_called_with('Attempting to remove verify match entry with PID = 200abc123')
        mock_logger_error.assert_called_with('no match found for PID: nothing removed')

    @mock.patch('application.borrower.views.VerifyMatch.remove_verify_match', autospec=True)
    @mock.patch('application.borrower.views.jsonify')
    @mock.patch('application.borrower.views.application.app.logger.debug')
    def test_delete_verify_match_true(self, mock_logger_debug, mock_jsonify, mock_verify_match):
        mock_jsonify.return_value = 'match found for PID 200abc123: row removed'
        mock_verify_match.return_value = True
        self.assertEqual(delete_verify_match('200abc123'), ('match found for PID 200abc123: row removed', 200))
        mock_logger_debug.assert_called_with('match found for PID: row removed')

    @mock.patch('application.borrower.views.jsonify')
    @mock.patch('application.borrower.views.Borrower.get_by_token')
    def test_check_borrower_signing_in_progress(self, mock_borrower, mock_jsonify):
        class ReturnedBorrower:
            id = 0000000
            token = "aaaaaa"
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            phonenumber = "07777777777"
            signing_in_progress = True

        mock_borrower.return_value = ReturnedBorrower()
        mock_jsonify.return_value = {'result': 'Signing in progress'}
        self.assertEqual(check_borrower_signing_in_progress('aaaaaa'), ({'result': 'Signing in progress'}, 200))

    @mock.patch('application.borrower.views.Borrower.save')
    @mock.patch('application.borrower.views.Borrower.get_by_token')
    def test_update_borrower_signing_in_progress(self, mock_borrower_save, mock_borrower):
        class ReturnedBorrower:
            id = 0000000
            token = "aaaaaa"
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            phonenumber = "07777777777"
            signing_in_progress = False

        mock_borrower.return_value = ReturnedBorrower()
        mock_borrower_save.signing_in_progress = True
        self.assertEqual(update_borrower_signing_in_progress('aaaaaa'), ('Borrower signing_in_progress set to true', 200))
