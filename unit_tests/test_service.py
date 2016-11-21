import unittest
import mock
from application import app
from unit_tests.helper import MortgageDocMock, MortgageDocMockWithReference, DeedHelper, DeedModelMock
from application.deed.service import update_md_clauses, update_deed
from application.deed.model import Deed
import json


class TestService(unittest.TestCase):

    def setUp(self):
        app.config.from_pyfile("config.py")
        self.app = app.test_client()

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_no_deed_result(self, mock_query):

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = None

        self.assertEqual(update_md_clauses(None, "e-MDTest", "RefTest", "Fake Org"), False)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_no_lender_reference_name(self, mock_query):

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMock()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "Fake reference", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMock.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.'}

        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_with_lender_reference_name(self, mock_query):

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

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_with_lender_reference_name_but_no_reference(self, mock_query):

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMockWithReference()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMockWithReference.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.'}

        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.assign_deed')
    @mock.patch('application.deed.service.delete_orphaned_borrowers')
    @mock.patch('application.borrower.model.Borrower')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.deed.service.update_md_clauses', autospec=True)
    @mock.patch('application.deed.service.update_borrower')
    @mock.patch('application.deed.service.build_json_deed_document')
    def test_update_deed_with_reference(self, mock_json_doc, mock_updated_borrower, mock_update_md, mock_save_deed,
                                        mock_borrower, mock_delete_orphans, mock_assign):

        new_deed = Deed()

        mock_json_doc.return_value = DeedHelper._valid_initial_deed
        mock_updated_borrower.return_value = DeedHelper._valid_single_borrower_update_response

        res, msg = update_deed(new_deed, DeedHelper._json_doc_with_reference)

        mock_assign.assert_called_with(new_deed, DeedHelper._update_deed_mock_response)

        mock_update_md.assert_called_with(DeedHelper._valid_initial_deed,
                                          DeedHelper._json_doc_with_reference['md_ref'],
                                          DeedHelper._json_doc_with_reference['reference'],
                                          None)

        self.assertTrue(res)

    @mock.patch('application.deed.service.assign_deed')
    @mock.patch('application.deed.service.delete_orphaned_borrowers')
    @mock.patch('application.borrower.model.Borrower')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.deed.service.update_md_clauses', autospec=True)
    @mock.patch('application.deed.service.update_borrower')
    @mock.patch('application.deed.service.build_json_deed_document')
    def test_update_deed(self, mock_json_doc, mock_updated_borrower, mock_update_md, mock_save_deed, mock_borrower, mock_delete_orphans, mock_assign):
        new_deed = DeedModelMock()

        mock_json_doc.return_value = DeedHelper._valid_initial_deed
        mock_updated_borrower.return_value = DeedHelper._valid_single_borrower_update_response

        res, msg = update_deed(new_deed, DeedHelper._json_doc)

        mock_assign.assert_called_with(new_deed, DeedHelper._update_deed_mock_response)

        self.assertTrue(res)

    @mock.patch('application.borrower.model.Borrower')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.deed.service.update_md_clauses')
    @mock.patch('application.deed.service.update_borrower')
    @mock.patch('application.deed.service.build_json_deed_document')
    def test_update_deed_invalid(self, mock_json_doc, mock_updated_borrower, mock_update_md, mock_save_deed, mock_borrower):
        new_deed = DeedModelMock()

        mock_json_doc.return_value = DeedHelper._valid_initial_deed
        mock_updated_borrower.return_value = DeedHelper._valid_single_borrower_update_response

        mock_update_md.return_value = None

        res, msg = update_deed(new_deed, DeedHelper._json_doc)

        self.assertFalse(res)
