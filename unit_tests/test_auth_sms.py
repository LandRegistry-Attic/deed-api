import unittest
import mock
from unittest.mock import patch, MagicMock
from application.deed.views import auth_sms
from application import app
from flask.ext.api import status


class TestAuthSms(unittest.TestCase):

    @mock.patch('application.deed.model.Deed.get_deed')
    @mock.patch('application.deed.views.abort')
    def test_auth_sms_deed_not_found(self, mock_abort, mock_get_deed):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_get_deed.return_value = None
                auth_sms("11", "11", "11")
                mock_abort.assert_called_with(status.HTTP_404_NOT_FOUND)
