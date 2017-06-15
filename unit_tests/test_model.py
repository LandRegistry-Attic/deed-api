from builtins import FileNotFoundError
import unittest
import mock

from application.deed.model import Deed, deed_json_adapter, deed_adapter, deed_pdf_adapter


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

    @mock.patch('application.deed.model.Deed.get_deed_system')
    def test_get_deed_adapter_use_system(self, mock_get_deed_system):
        deed = Deed()
        deed.deed = {}
        deed.token = 'token'
        deed.status = 'status'
        mock_get_deed_system.return_value = deed
        result = deed_adapter('1234', True)
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

    @mock.patch('application.deed.model.Deed.get_deed')
    def test_deed_pdf_adapter(self, mock_get_deed):
        deed = Deed()
        deed.deed = {"effective_date": "2016-07-05 12:00:05",
                     "property_address": "0 The Drive, This Town, This County, PL0 0TH"}
        deed.token = 'token'
        deed.status = 'status'
        mock_get_deed.return_value = deed
        result = deed_pdf_adapter('1234')
        self.assertEqual(deed.token, result['token'])
        self.assertEqual(deed.status, result['status'])
        self.assertEqual('05/07/2016', result['effective_date'])
        self.assertEqual(['0 The Drive', 'This Town', 'This County', 'PL0 0TH'], result['property_address'])

    @mock.patch('application.deed.model.Deed.get_deed_system')
    def test_deed_pdf_adapter_use_system(self, mock_get_deed_system):
        deed = Deed()
        deed.deed = {"effective_date": "2016-07-05 12:00:05",
                     "property_address": "0 The Drive, This Town, This County, PL0 0TH"}
        deed.token = 'token'
        deed.status = 'status'
        mock_get_deed_system.return_value = deed
        result = deed_pdf_adapter('1234', True)
        self.assertEqual(deed.token, result['token'])
        self.assertEqual(deed.status, result['status'])
        self.assertEqual('05/07/2016', result['effective_date'])
        self.assertEqual(['0 The Drive', 'This Town', 'This County', 'PL0 0TH'], result['property_address'])

    @mock.patch('application.deed.model.Deed.get_deed_system')
    @mock.patch('application.deed.model.Deed.get_deed')
    def test_deed_adapter_use_system_alternative(self, mock_get_deed, mock_get_deed_system):
        # Check that a use_system value of True calls get_deed_system
        deed_pdf_adapter('1234', True)
        mock_get_deed_system.assert_called_with('1234')

        # Check that a use_system value of False calls get_deed
        deed_pdf_adapter('1234', False)
        mock_get_deed.assert_called_with('1234')
