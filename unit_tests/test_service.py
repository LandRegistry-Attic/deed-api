import unittest
import mock
from application import app
from unit_tests.helper import MortgageDocMock, MortgageDocMockWithReference
from application.deed.service import update_md_clauses
import json


class TestService(unittest.TestCase):

    def setUp(self):
        app.config.from_pyfile("config.py")
        self.app = app.test_client()

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_no_result(self, mock_query):

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = None

        self.assertEqual(update_md_clauses(None, "e-MDTest", "RefTest", "Fake Org"), False)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_no_reference(self, mock_query):

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMock()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "Fake Bank", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMock.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.'}

        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_with_reference(self, mock_query):

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMockWithReference()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "Fake Bank", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMockWithReference.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.',
                         'reference_details':
                             {'lender_reference_name': md_dict['lender_reference_name'],
                              'lender_reference_value': 'Fake Bank'}
                         }

        self.assertEquals(mock_dict, expected_dict)
