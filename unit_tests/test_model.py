__author__ = 'paultrelease'

import unittest

import mock


from application.deed.model import Deed, get_enriched_deed
from unit_tests.helper import DeedModelMock

class TestDeed(unittest.TestCase):

    def test_get_deed_not_found(self):
        deed = Deed()
        def _get_deed_mock(*args):
            return None
        deed.get_deed = _get_deed_mock
        self.assertRaises(FileNotFoundError, get_enriched_deed, 'ref')

    def _test_get_deed(self):
        deed = Deed()
        def _get_deed_mock(*args):
            return DeedModelMock()
        deed.get_deed = _get_deed_mock
        result = get_enriched_deed('1234')
        self.assertEqual(result.token, result.deed['token'])
        self.assertEqual(result.status, result.deed['status'])