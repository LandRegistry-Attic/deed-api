import unittest
import mock

from application.deed.model import Deed, deed_json_adapter, deed_adapter


class TestDeed(unittest.TestCase):

    @mock.patch('application.deed.model.Deed.get_deed')
    def test_get_deed_not_found(self, mock_get_deed):
        mock_get_deed.return_value = None
        self.assertRaises(FileNotFoundError, deed_json_adapter, 'ref')


    @mock.patch('application.deed.model.Deed.get_deed')
    def test_get_deed_adapter(self, mock_get_deed):
        deed = Deed()
        deed.deed = {}
        deed.token = 'token'
        deed.status = 'status'
        mock_get_deed.return_value = deed
        result = deed_adapter('1234')
        self.assertEqual(deed.token, result.token)
        self.assertEqual(deed.status, result.status)

    @mock.patch('application.deed.model.Deed.get_deed')
    def test_get_deed_json_adapter(self, mock_get_deed):
        deed = Deed()
        deed.deed = {}
        deed.token = 'token'
        deed.status = 'status'
        mock_get_deed.return_value = deed
        result = deed_json_adapter('1234')
        self.assertEqual(deed.token, result['deed']['token'])
        self.assertEqual(deed.status, result['deed']['status'])