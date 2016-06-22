__author__ = 'paultrelease'

import unittest

import mock


from application.deed.model import Deed, get_enriched_deed

class TestDeed(unittest.TestCase):

    @mock.patch('application.deed.model.Deed.get_deed')
    def test_get_deed_not_found(self, mock_get_deed):
        mock_get_deed.return_value = None
        self.assertRaises(FileNotFoundError, get_enriched_deed, 'ref')


    @mock.patch('application.deed.model.Deed.get_deed')
    def test_get_deed(self, mock_get_deed):
        deed = Deed()
        deed.deed = {}
        deed.token = 'token'
        deed.status = 'status'
        mock_get_deed.return_value = deed
        result = get_enriched_deed('1234')
        self.assertEqual(deed.token, result['token'])
        self.assertEqual(deed.status, result['status'])