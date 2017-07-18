import unittest
import mock
from application.deed.views import auth_sms
from application import app
from unit_tests.helper import DeedModelMock, BorrowerModelMock, BorrowerModelMockNoId, EsecClientMock
from werkzeug.exceptions import NotFound, InternalServerError


class TestAuthSms(unittest.TestCase):

    @mock.patch('application.deed.views.Deed.get_deed')
    def test_auth_sms_deed_not_found(self, mock_get_deed):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_get_deed.return_value = None

                with self.assertRaises(NotFound):
                    auth_sms("11", "11", "11")

    @mock.patch('application.deed.views.Akuma.do_check')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_auth_sms_akuma_result_z(self, mock_get_deed, mock_akuma):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_get_deed.return_value = DeedModelMock()
                mock_akuma.return_value = {
                    "result": "Z",
                    "id": "2b9115b2-d956-11e5-942f-08002719cd16"
                }
                result = auth_sms("11", "11", "11")
                self.assertEqual(result, 'Failed to sign Mortgage document')

    @mock.patch('application.deed.views.Akuma.do_check')
    @mock.patch('application.deed.views.Deed.get_borrower_position')
    @mock.patch('application.deed.views.convert_json_to_xml')
    @mock.patch('application.deed.views.Borrower.get_by_token')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_auth_sms_no_esec_id(self, mock_get_deed, mock_get_borrower, mock_convert_json, mock_borrower_pos,
                                 mock_akuma):
        mock_get_borrower.return_value = BorrowerModelMock
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_get_deed.return_value = DeedModelMock()
                with self.assertRaises(InternalServerError):
                    auth_sms("11", "11", "11")

    @mock.patch('application.deed.views.make_esec_client')
    @mock.patch('application.deed.views.Akuma.do_check')
    @mock.patch('application.deed.views.Deed.get_borrower_position')
    @mock.patch('application.deed.views.convert_json_to_xml')
    @mock.patch('application.deed.views.Borrower.get_by_token')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_auth_sms_happy_path(self, mock_get_deed, mock_get_borrower, mock_convert_json, mock_borrower_pos,
                                 mock_akuma, mock_esec_client):
        mock_get_borrower.return_value = BorrowerModelMockNoId
        mock_esec_client.return_value = EsecClientMock()
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_get_deed.return_value = DeedModelMock()

                resp = auth_sms("11", "11", "11")

                self.assertEqual(resp[1], 200)
