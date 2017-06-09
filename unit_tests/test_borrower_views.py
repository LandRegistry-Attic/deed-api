import unittest
import mock
from application.borrower.views import delete_verify_match


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
