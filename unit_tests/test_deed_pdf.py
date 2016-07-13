import unittest
import mock

from application import app
from application.deed.deed_render import create_deed_html
from unit_tests.helper import DeedModelMock


class TestDeedPdf(unittest.TestCase):

    @mock.patch('application.deed.address_utils.format_address_string')
    def test_create_deed_html(self, mock_format):
        deed = DeedModelMock
        mock_format.return_value = 'a house'
        with app.app_context():
            self.assertTrue('Digital Mortgage Deed' in create_deed_html(deed.deed))
            self.assertTrue('e-MD12344' in create_deed_html(deed.deed))
