import unittest
import mock
from unittest.mock import patch, MagicMock
from application.deed.views import auth_sms
from application import app
from flask.ext.api import status

class TestAuthSms(unittest.TestCase):

    @mock.patch('application.deed.views.abort')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_auth_sms_deed_not_found(self, mock_deed, mock_abort):
        mock_deed.return_value = None

        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():

                resp = auth_sms("11", "11", "11")

            self.assertTrue(resp)

            mock_abort.assert_called_with(status.HTTP_404_NOT_FOUND)
