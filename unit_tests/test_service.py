import json
import mock
import unittest
from application.deed.model import Deed
from application.deed.service import update_md_clauses, update_deed

from application import app
from unit_tests.helper import MortgageDocMock, MortgageDocMockWithReference, MortgageDocMockWithDateOfMortgageOffer,\
    MortgageDocMockWithMiscInfo, DeedHelper


class TestService(unittest.TestCase):

    def setUp(self):
        app.config.from_pyfile("config.py")
        self.app = app.test_client()

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_no_deed_result(self, mock_query):

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = None

        self.assertEqual(update_md_clauses(None, "e-MDTest", "RefTest", "", "", "Fake Org"), False)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_no_lender_reference_name(self, mock_query):
        # The mortgage doc has no reference specified - but the function receives one.
        # As a result, NO reference should appear in the outputted deed.

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMock()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "Fake reference", "", "", "Fake Org"), True)

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
        # The mortgage doc has a reference specified - and the function receives a reference.
        # As a result, the reference should appear in the outputted deed.

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMockWithReference()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "Fake Bank", "", "", "Fake Org"), True)

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
        # The mortgage doc has a reference specified - but the function receives NO reference.
        # As a result, NO reference should appear in the outputted deed.

        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMockWithReference()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "", "", "", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMockWithReference.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.'}

        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_no_date_of_mortgage_offer(self, mock_query):
        # The mortgage doc has no mortgage date offer - but the function receives one.
        # As a result, NO mortgage document offer date should appear in the outputted deed.
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMock()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "", "a mortgage date offer", "", "Fake Org"),
                         True)

        md_dict = json.loads(MortgageDocMock.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.'}

        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_with_date_of_mortgage_offer(self, mock_query):
        # The mortgage doc includes the mortgage date offer - and a mortgage date offer is provided to the function.
        # As a result, mortgage document offer date should appear in the outputted deed.
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMockWithDateOfMortgageOffer()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "", "a mortgage date offer", "", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMockWithDateOfMortgageOffer.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.',
                         'date_of_mortgage_offer_details':
                             {'date_of_mortgage_offer_heading': md_dict['date_of_mortgage_offer_heading'],
                              'date_of_mortgage_offer_value': 'a mortgage date offer'}
                         }
        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_with_date_of_mortgage_offer_heading_but_no_info_from_deed(self, mock_query):
        # The mortgage doc includes the mortgage date offer - but no mortgage date offer is provided to the function.
        # As a result, mortgage document offer date should NOT appear in the outputted deed.
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMockWithReference()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "", "", "", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMockWithDateOfMortgageOffer.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.'}

        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_no_miscellaneous_information(self, mock_query):
        # The mortgage doc has no misc info - but the function receives some.
        # As a result, NO misc info should appear in the outputted deed.
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMock()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "", "", "some misc info", "Fake Org"),
                         True)

        md_dict = json.loads(MortgageDocMock.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.'}

        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_with_misc_info(self, mock_query):
        # The mortgage doc includes misc info - and a mortgage date offer is provided misc info
        # As a result, misc info should appear in the outputted deed.
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMockWithMiscInfo()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "", "", "some misc info", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMockWithMiscInfo.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.',
                         'miscellaneous_information_details':
                             {'miscellaneous_information_heading': md_dict['miscellaneous_information_heading'],
                              'miscellaneous_information_value': 'some misc info'}
                         }
        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.MortgageDocument.query', autospec=True)
    def test_update_md_clauses_with_misc_info_but_no_info_from_deed(self, mock_query):
        # The mortgage doc includes the misc info - but no misc is provided to the function.
        # As a result, misc info should NOT appear in the outputted deed.
        mock_query_response = mock_query.filter_by.return_value
        mock_query_response.first.return_value = MortgageDocMockWithMiscInfo()

        mock_dict = {}

        self.assertEqual(update_md_clauses(mock_dict, "e-MDTest", "", "", "", "Fake Org"), True)

        md_dict = json.loads(MortgageDocMockWithMiscInfo.data)

        expected_dict = {'charge_clause': md_dict['charge_clause'],
                         'additional_provisions': md_dict['additional_provisions'],
                         'lender': md_dict['lender'],
                         'effective_clause': 'This charge takes effect when the registrar' +
                                             ' receives notification from Fake Org that the charge' +
                                             ' is to take effect.'}

        self.assertEquals(mock_dict, expected_dict)

    @mock.patch('application.deed.service.assign_deed')
    @mock.patch('application.deed.service.delete_orphaned_borrowers')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.deed.service.update_md_clauses', autospec=True)
    @mock.patch('application.deed.service.update_borrower')
    @mock.patch('application.deed.service.build_json_deed_document')
    @mock.patch('application.deed.service.get_organisation_name')
    def test_update_deed_with_reference(self, mock_org_name, mock_json_doc, mock_updated_borrower, mock_update_md,
                                        mock_save_deed,
                                        mock_delete_orphans, mock_assign):
        new_deed = Deed()
        mock_org_name.return_value = 'A conveyancer'
        new_deed.organisation_id = "1"
        new_deed.organisation_name = mock_org_name
        mock_json_doc.return_value = DeedHelper._valid_initial_deed
        mock_updated_borrower.return_value = DeedHelper._valid_single_borrower_update_response

        res, msg = update_deed(new_deed, DeedHelper._json_doc_with_reference)

        mock_assign.assert_called_with(new_deed, DeedHelper._update_deed_mock_response)

        mock_update_md.assert_called_with(DeedHelper._valid_initial_deed,
                                          DeedHelper._json_doc_with_reference["md_ref"],
                                          DeedHelper._json_doc_with_reference["reference"],
                                          "",
                                          "",
                                          'A conveyancer')

        self.assertTrue(res)

    @mock.patch('application.deed.service.assign_deed')
    @mock.patch('application.deed.service.delete_orphaned_borrowers')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.deed.service.update_md_clauses', autospec=True)
    @mock.patch('application.deed.service.update_borrower')
    @mock.patch('application.deed.service.build_json_deed_document')
    @mock.patch('application.deed.service.get_organisation_name')
    def test_update_deed(self, mock_org_name, mock_json_doc, mock_updated_borrower, mock_update_md, mock_save_deed, mock_delete_orphans, mock_assign):
        new_deed = Deed()
        mock_org_name.return_value = 'A conveyancer'
        new_deed.organisation_id = "1"
        new_deed.organisation_name = mock_org_name

        mock_json_doc.return_value = DeedHelper._valid_initial_deed
        mock_updated_borrower.return_value = DeedHelper._valid_single_borrower_update_response

        res, msg = update_deed(new_deed, DeedHelper._json_doc)

        mock_assign.assert_called_with(new_deed, DeedHelper._update_deed_mock_response)

        self.assertTrue(res)

    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.deed.service.update_md_clauses')
    @mock.patch('application.deed.service.update_borrower')
    @mock.patch('application.deed.service.build_json_deed_document')
    @mock.patch('application.deed.service.get_organisation_name')
    def test_update_deed_invalid(self, mock_org_name, mock_json_doc, mock_updated_borrower, mock_update_md, mock_save_deed):
        new_deed = Deed()
        mock_org_name.return_value = 'A conveyancer'
        new_deed.organisation_id = "1"
        new_deed.organisation_name = mock_org_name

        mock_json_doc.return_value = DeedHelper._valid_initial_deed
        mock_updated_borrower.return_value = DeedHelper._valid_single_borrower_update_response

        mock_update_md.return_value = None

        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                res, msg = update_deed(new_deed, DeedHelper._json_doc)
                self.assertFalse(res)
