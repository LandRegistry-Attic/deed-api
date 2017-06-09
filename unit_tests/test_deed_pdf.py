import unittest
import mock

from application import app
from application.deed.deed_render import create_deed_html
from unit_tests.helper import DeedModelMock, MortgageDocMockWithDateOfMortgageOffer, MortgageDocMockWithMiscInfo


class TestDeedPdf(unittest.TestCase):

    @mock.patch('application.deed.address_utils.format_address_string')
    def test_create_deed_html(self, mock_format):
        deed = DeedModelMock
        mock_format.return_value = 'a house'
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                self.assertTrue('Digital Mortgage Deed' in create_deed_html(deed.deed))
                self.assertTrue('e-MD12344' in create_deed_html(deed.deed))

    @mock.patch('application.deed.address_utils.format_address_string')
    def test_create_deed_html_with_date_of_mortgage_offer(self, mock_format):
        deed = MortgageDocMockWithDateOfMortgageOffer
        mock_format.return_value = 'a house'
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                self.assertTrue('Digital Mortgage Deed' in create_deed_html(deed.deed))
                self.assertTrue('e-MD1291A' in create_deed_html(deed.deed))
                self.assertTrue('Date of Mortgage Offer' in create_deed_html(deed.deed))
                self.assertTrue('a date string' in create_deed_html(deed.deed))

    @mock.patch('application.deed.address_utils.format_address_string')
    def test_create_deed_html_with_misc_info(self, mock_format):
        deed = MortgageDocMockWithMiscInfo
        mock_format.return_value = 'a house'
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                # Do not display the misc info, as we don't know where that is going in the template yet.
                # Even though the misc info information exits in the constructed deed.
                self.assertTrue('Digital Mortgage Deed' in create_deed_html(deed.deed))
                self.assertTrue('e-MD1291A' in create_deed_html(deed.deed))
                self.assertFalse('Your conveyancer contact is' in create_deed_html(deed.deed))
                self.assertFalse('bob test' in create_deed_html(deed.deed))
