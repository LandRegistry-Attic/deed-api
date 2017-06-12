import PyPDF2
import io
import os
import json
import mock
import requests  # NOQA
import unittest
from application.akuma.service import Akuma
from application.casework.service import get_document
from application.deed.deed_validator import Validation
from application.deed.model import Deed
from application.deed.service import apply_registrar_signature, check_effective_status, add_effective_date_to_xml
from application.deed.service import make_effective_text, make_deed_effective_date
from application.deed.utils import convert_json_to_xml, validate_generated_xml
from application.deed.views import make_effective, retrieve_signed_deed
from datetime import datetime
from flask.ext.api import status
from lxml import etree
from unittest.mock import patch, MagicMock

from application import app
from application.borrower.model import Borrower, DatabaseException
from application.service_clients.esec.implementation import sign_document_with_authority, _post_request, ExternalServiceError, EsecException
from application.service_clients.organisation_adapter.implementation import get_organisation_name
from unit_tests.helper import DeedHelper, DeedModelMock, MortgageDocMock, StatusMock, FakeResponse
from unit_tests.schema_tests import run_schema_checks


class TestRoutesBase(unittest.TestCase):
    DEED_ENDPOINT = "/deed/"
    DEED_QUERY = "/deed"
    BORROWER_ENDPOINT = "/borrower/"
    CASEWORK_ENDPOINT = "/casework/"

    non_webseal_headers = {
        "Content-Type": "application/json"
    }
    webseal_headers = {
        "Content-Type": "application/json",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv('WEBSEAL_HEADER_VALUE')
    }
    dodgy_webseal_headers1 = {
        "Content-Type": "application/json",
        os.getenv('WEBSEAL_HEADER_KEY'): "incorrect data"
    }

    def setUp(self):
        app.config.from_pyfile("config.py")
        self.app = app.test_client()


class TestRoutes(TestRoutesBase):

    def test_health(self):
        self.assertEqual((self.app.get('/health')).status_code,
                         status.HTTP_200_OK)

    def test_health_service_check(self):
        self.assertEqual((self.app.get('/health/service-check')).status_code,
                         status.HTTP_200_OK)

    def test_deed(self):
        self.assertEqual((self.app.get('/deed')).status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_status_with_invalid_params(self):
        self.assertEqual((self.app.get('/deed?invalid=invalid')).status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_model(self):
        test_deed = Deed()
        test_token = test_deed.generate_token()
        self.assertTrue(len(test_token) == 36)

    @patch('application.deed.model.Deed.save')
    @patch('application.service_clients.esec.implementation.sign_document_with_authority')
    def test_sign_document_is_called(self, mock_sign_with_authority, mock_save):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_deed = DeedModelMock()
                mock_deed.status = "NOT-LR-SIGNED"
                effective_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                apply_registrar_signature(mock_deed, effective_date)
                self.assertTrue(mock_sign_with_authority.called)
                self.assertTrue(mock_save.called)

    def test_effective_date_in_xml(self):
        mock_deed = DeedModelMock()
        effective_date = '1922-02-02 00:00:00'

        result = add_effective_date_to_xml(mock_deed.deed_xml, effective_date)

        mock_xml = etree.fromstring(result)
        for val in mock_xml.xpath("/dm-application/effectiveDate"):
            test_result = val.text

        self.assertEqual(effective_date, test_result)

    def test_wrong_effective_status(self):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_deed = DeedModelMock()
                self.assertRaises(ValueError, check_effective_status, mock_deed.status)

    def test_post_request_200(self):

        with app.app_context() as ac:

            def fake_post(url, data):
                return FakeResponse(content='I have returned with a 200')

            ac.g.trace_id = None

            # Create a MagicMock and assign it to the g.requests function
            mock_requests = MagicMock()
            ac.g.requests = mock_requests

            # Create a MagicMock and assign it to the g.requests.post function
            mock_post = MagicMock()
            mock_post.side_effect = fake_post
            ac.g.requests.post = mock_post

            # Call the assertion for the test
            mock_deed = DeedModelMock()
            ret_val = _post_request('dummy/url/string', mock_deed.deed_xml)

            self.assertEqual('I have returned with a 200', ret_val)

    def test_post_request_500(self):

        with app.app_context() as ac:

            def fake_post(url, data):
                fake_response = FakeResponse(content='I have returned with a 500')
                fake_response.status_code = 500
                return fake_response

            ac.g.trace_id = None

            # Create a MagicMock and assign it to the g.requests function
            mock_requests = MagicMock()
            ac.g.requests = mock_requests

            # Create a MagicMock and assign it to the g.requests.post function
            mock_post = MagicMock()
            mock_post.side_effect = fake_post
            ac.g.requests.post = mock_post

            # Call the assertion for the test
            mock_deed = DeedModelMock()
            self.assertRaises(ExternalServiceError,
                              _post_request, 'dummy/url/string', mock_deed.deed_xml)

    @patch('application.service_clients.esec.implementation._post_request')
    def test_sign_document_with_authority(self, mock_post_request):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_deed = DeedModelMock()
                sign_document_with_authority(mock_deed.deed_xml)
                mock_post_request.assert_called_with('{}/esec/sign_document_with_authority'
                                                     .format(app.config["ESEC_CLIENT_BASE_HOST"]),
                                                     mock_deed.deed_xml)

    @mock.patch('application.deed.views.Validation.validate_organisation_credentials')
    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.mortgage_document.model.MortgageDocument.query', autospec=True)
    def test_create_no_auth_headers(self, mock_query, mock_Deed, mock_Borrower, mock_akuma, mock_proprietor_names,
                                    mock_organisation_cred):
        mock_organisation_cred.return_value = None

        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = MortgageDocMock()
        mock_proprietor_names.return_value = ['lisa ann bloggette', 'frank ann bloggette']
        mock_akuma.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }
        payload = json.dumps(DeedHelper._json_doc)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch('application.borrower.model.Borrower')
    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.title_adaptor.service.TitleAdaptor.do_check', autospec=False)
    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.mortgage_document.model.MortgageDocument.query', autospec=True)
    @mock.patch('application.deed.service.get_organisation_name')
    def test_create_webseal_external(self, mock_organisation_name, mock_query, mock_Deed, mock_Borrower, mock_akuma,
                                     mock_title, mock_proprietor_names, mock_borrower):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = MortgageDocMock()
        mock_akuma.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }

        mock_proprietor_names.return_value = ['lisa ann bloggette', 'frank ann bloggette']
        payload = json.dumps(DeedHelper._json_doc)
        mock_title.return_value = "title OK"
        payload = json.dumps(DeedHelper._json_doc)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.mortgage_document.model.MortgageDocument.query', autospec=True)
    def test_create_webseal_external_dodgy_headers1(self, mock_query, mock_Deed, mock_Borrower, mock_akuma, mock_proprietor_names):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = MortgageDocMock()
        mock_akuma.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }
        mock_proprietor_names.return_value = ['lisa ann bloggette', 'frank ann bloggette']
        payload = json.dumps(DeedHelper._json_doc)
        payload = json.dumps(DeedHelper._json_doc)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers=self.dodgy_webseal_headers1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch('application.deed.deed_validator.Validation.validate_organisation_credentials')
    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    def test_create_with_invalid_phone_numbers(self, mock_Borrower, mock_Deed, mock_proprietor_names, mock_organisation_cred):
        mock_organisation_cred.return_value = {'organisation_id': "Foo",
                                               'organisation_name': "Bar",
                                               'organisation_locale': "FooBar"}

        mock_proprietor_names.return_value = ['lisa bloggette', 'frank bloggette']
        payload = json.dumps(DeedHelper._invalid_phone_numbers)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_fails_with_borrower_ids(self):

        # A test to ensure that if a deed is being created (not updated) and the borrowers
        # have id's included in the payload, that the system prevents it from being created
        payload = DeedHelper._valid_borrowers_with_ids

        validator = Validation()
        validate_borrowers, msg = validator.validate_borrower_ids(payload)

        self.assertEqual(validate_borrowers, False)
        self.assertEqual(msg, "A borrower id cannot be provided for this type of request.")

    def test_create_succeeds_with_borrower_ids(self):

        # A test to ensure that if a deed is being created (not updated) and the borrowers
        # ids are not included in the payload, that no error is reported
        payload = DeedHelper._json_doc

        validator = Validation()
        validate_borrowers, msg = validator.validate_borrower_ids(payload)

        self.assertEqual(validate_borrowers, True)
        self.assertEqual(msg, "")

    @mock.patch('application.deed.deed_validator.Validation.validate_organisation_credentials')
    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    def test_create_with_invalid_blanks(self, mock_Borrower, mock_Deed, mock_proprietor_names, mock_organisation_cred):
        mock_organisation_cred.return_value = {'organisation_id': "Foo",
                                               'organisation_name': "Bar",
                                               'organisation_locale': "FooBar"}

        payload = json.dumps(DeedHelper._invalid_blanks_on_required_fields)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.deed.deed_validator.Validation.validate_organisation_credentials')
    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    def test_invalid_title_format(self, mock_organisation_cred, mock_proprietor_names):
        mock_organisation_cred.return_value = {'organisation_id': "Foo",
                                               'organisation_name': "Bar",
                                               'organisation_locale': "FooBar"}

        payload = json.dumps(DeedHelper._invalid_title)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.deed.model.Deed.get_deed_status', autospec=True)
    def test_get_status_with_mdref_and_titleno_endpoint(self, get_deed_status):
        get_deed_status.return_value = StatusMock()._status_with_mdref_and_titleno

        response = self.app.get(self.DEED_QUERY + '?md_ref=e-MD12344&title_number=DN100')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("DRAFT" in response.data.decode())
        self.assertTrue("c91d57" in response.data.decode())

    @mock.patch('application.deed.model.Deed.get_deed_status', autospec=True)
    def test_get_no_status_with_mdref_and_titleno_endpoint_no_status(self, get_deed_status):
        get_deed_status.return_value = StatusMock()._no_status_with_mdref_and_titleno

        response = self.app.get(self.DEED_QUERY + '?md_ref=e-MD12344&title_number=DN100')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('application.borrower.model.Borrower.delete')
    def test_delete_borrower(self, mock_borrower):
        mock_borrower.return_value = DeedHelper._valid_borrowers
        response = self.app.delete(self.DEED_ENDPOINT + "borrowers/delete/1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('application.borrower.model.Borrower.delete')
    def test_delete_borrower_not_found(self, mock_borrower):
        mock_borrower.return_value = None
        response = self.app.delete(self.DEED_ENDPOINT + "borrowers/delete/99999")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('application.borrower.model.Borrower.get_by_token')
    def test_validate_borrower(self, mock_borrower):
        class ReturnedBorrower:
            id = 000000
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            phonenumber = "07777777777"

        mock_borrower.return_value = ReturnedBorrower()
        payload = json.dumps(DeedHelper._validate_borrower)
        response = self.app.post(self.BORROWER_ENDPOINT + "validate",
                                 data=payload,
                                 headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('application.borrower.model.Borrower.get_by_token')
    def test_validate_borrower_no_leading_zero(self, mock_borrower):
        class ReturnedBorrower:
            id = 0000000
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            phonenumber = "07777777777"

        mock_borrower.return_value = ReturnedBorrower()
        payload = json.dumps(DeedHelper._validate_borrower_dob)
        response = self.app.post(self.BORROWER_ENDPOINT + "validate",
                                 data=payload,
                                 headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test get borrower by PID (vaidate)
    @mock.patch('application.borrower.model.Borrower.get_by_verify_pid')
    def test_validate_borrower_by_pid(self, mock_borrower):
        class ReturnedBorrower:
            id = 0000000
            token = "aaaaaa"
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            phonenumber = "07777777777"

        mock_borrower.return_value = ReturnedBorrower()
        response = self.app.get(self.BORROWER_ENDPOINT + "verify/pid/1234")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('application.borrower.model.Borrower.get_by_token')
    def test_validate_borrower_not_found(self, mock_borrower):
        mock_borrower.return_value = None
        payload = json.dumps(DeedHelper._validate_borrower)

        response = self.app.post(self.BORROWER_ENDPOINT + "validate",
                                 data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.decode(), "Matching deed not found")

    @mock.patch('application.deed.deed_validator.Validation.validate_organisation_credentials')
    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    def test_create_with_invalid_address(self, mock_Borrower, mock_Deed, mock_proprietor_names, mock_organisation_cred):
        mock_organisation_cred.return_value = {'organisation_id': "Foo",
                                               'organisation_name': "Bar",
                                               'organisation_locale': "FooBar"}

        payload = json.dumps(DeedHelper._invalid_blank_address)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_schema_checks(self):
        self.assertTrue(run_schema_checks())

    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.service_clients.title_adaptor.interface.TitleAdaptorInterface.perform_check')
    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    @mock.patch('application.deed.service', autospec=True)
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.mortgage_document.model.MortgageDocument.query', autospec=True)
    def test_invalid_md_ref(self, mock_query, mock_Deed, mock_Borrower, mock_update, mock_akuma, mock_validator, mock_proprietor_names):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = None

        mock_akuma.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }
        mock_update.update_deed.return_value = True, "OK"
        mock_validator.return_value.text = "title OK"

        payload = json.dumps(DeedHelper._json_doc)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers=self.webseal_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_xml_generation(self):
        xml = convert_json_to_xml(DeedModelMock().deed)
        res = validate_generated_xml(xml)
        self.assertEqual(res, True)

    def test_get_document(self):
        with app.app_context():
            with app.test_request_context():
                resp = get_document()

                self.assertEqual(str(resp.mimetype), "application/pdf")

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_document_not_found(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = None

        response = self.app.get(self.CASEWORK_ENDPOINT + 'CD3456')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_document_from_endpoint(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()

        response = self.app.get(self.CASEWORK_ENDPOINT + 'AB1234')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("application/pdf" in response.mimetype)

    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    def test_akuma_check_create(self, mock_api):
        mock_api.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }

        check_result = Akuma.do_check(DeedHelper._json_doc, "create deed", "Test Organisation", "gb",
                                      "bb34300c-ba9b-4d86-b28f-ab793e0d45fa")

        self.assertEqual(check_result["result"], "A")

    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    def test_akuma_check_sign(self, mock_api):
        mock_api.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }

        check_result = Akuma.do_check(DeedHelper._json_doc, "borrower sign", "", "",
                                      "bb34300c-ba9b-4d86-b28f-ab793e0d45fa")

        self.assertEqual(check_result["result"], "A")

    def test_make_effective_clause(self):

        effective_clause = make_effective_text("Test Organisation")
        correct_effective_clause = "This charge takes effect when the registrar receives notification from " + \
                                   "Test Organisation that the charge is to take effect."

        self.assertEqual(effective_clause, correct_effective_clause)

    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.borrower.model.Borrower.get_by_token')
    @mock.patch('application.service_clients.esec.interface.EsecClientInterface.issue_sms')
    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_request_auth_code(self, mock_query, mock_issue, mock_borrower, mock_borrower_save):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()
        mock_issue.return_value = "DM212".encode(), 200

        class ReturnedBorrower(Borrower):
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            forename = "Jack"
            middlename = "John"
            surname = "Duck"

        mock_borrower.return_value = ReturnedBorrower()
        mock_borrower_save.return_value = "OK"

        payload = json.dumps(DeedHelper._add_borrower_signature)

        response = self.app.post(self.DEED_ENDPOINT + 'AB1234' + '/request-auth-code',
                                 data=payload,
                                 headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_issue.assert_called_with('Jack John', 'Duck', None, None)

    @mock.patch('application.borrower.model.Borrower.get_by_token')
    @mock.patch('application.service_clients.esec.interface.EsecClientInterface.reissue_sms')
    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_reissue_auth_code(self, mock_query, mock_reissue, mock_borrower):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()
        mock_reissue.return_value = "SUCCESS", 200

        class ReturnedBorrower(Borrower):
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            forename = "Jack"
            surname = "Duck"
            esec_user_name = "DM123"

        mock_borrower.return_value = ReturnedBorrower()

        payload = json.dumps(DeedHelper._add_borrower_signature)

        response = self.app.post(self.DEED_ENDPOINT + 'AB1234' + '/request-auth-code',
                                 data=payload,
                                 headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.borrower.model.Borrower.get_by_token')
    @mock.patch('application.deed.utils.get_borrower_position')
    @mock.patch('application.service_clients.esec.interface.EsecClientInterface.auth_sms')
    @mock.patch('application.deed.model.Deed.save', autospec=True)
    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_add_authenticate_and_sign(self, mock_query, mock_Deed_save,
                                       mock_auth, mock_position, mock_borrower, mock_borrower_save, mock_api):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()

        mock_api.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }

        class ReturnedBorrower(Borrower):
            deed_token = "aaaaaa"
            dob = "02/02/1922"
            forename = "Jack"
            middlename = "John"
            surname = "Duck"
            esec_user_name = "DM123"

        mock_borrower.return_value = ReturnedBorrower()

        mock_auth.return_value = "<p></p>", 200
        mock_position.return_value = 1
        mock_borrower_save.return_value = "OK"

        payload = json.dumps(DeedHelper._verify_and_sign)

        response = self.app.post(self.DEED_ENDPOINT + 'AB1234' + '/verify-auth-code',
                                 data=payload,
                                 headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_make_deed_effective_date(self):
        deed_model = mock.create_autospec(Deed)
        deed_model.deed = {}
        signed_time = 'a time'
        make_deed_effective_date(deed_model, signed_time)
        deed_model.save.assert_called_with()
        self.assertEqual(deed_model.deed['effective_date'], 'a time')

    @mock.patch('application.deed.model.Deed.get_deed')
    @mock.patch('application.deed.views.abort')
    def test_make_deed_effective_404(self, mock_abort, mock_get_deed):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                mock_get_deed.return_value = None
                make_effective(123)
                mock_abort.assert_called_with(status.HTTP_404_NOT_FOUND)

    @mock.patch('application.deed.model.Deed.get_deed')
    @mock.patch('application.deed.views.Akuma.do_check')
    @mock.patch('application.deed.views.datetime')
    @mock.patch('application.deed.views.apply_registrar_signature')
    def test_make_deed_effective(self, mock_sign, mock_datetime, mock_akuma, mock_get_deed):
        deed_model = mock.create_autospec(Deed)
        deed_model.deed = {}
        deed_model.status = "ALL-SIGNED"
        mock_datetime.now.return_value = datetime(1900, 1, 1)
        mock_get_deed.return_value = deed_model
        response = self.app.post(self.DEED_ENDPOINT + '123' + '/make-effective',
                                 headers=self.webseal_headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("path" in response.data.decode())

    @mock.patch('application.deed.model.Deed.get_deed')
    @mock.patch('application.deed.views.Akuma.do_check')
    @mock.patch('application.deed.views.jsonify')
    def test_make_deed_effective_400(self, mock_jsonify, mock_akuma, mock_get_deed):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                deed_model = mock.create_autospec(Deed)
                deed_model.deed = {}

                # test where already effective
                deed_model.status = "EFFECTIVE"
                mock_get_deed.return_value = deed_model
                response_status_code = make_effective(123)[1]
                mock_jsonify.assert_called_with({'errors': ['Problem 1: This deed has already been made effective.']})
                self.assertEqual(response_status_code, 400)

                # test where not registrar signed
                deed_model.status = "NOT-LR-SIGNED"
                mock_get_deed.return_value = deed_model
                response_status_code = make_effective(123)[1]
                mock_jsonify.assert_called_with({'errors': ['Problem 1: This deed has already been made effective.']})
                self.assertEqual(response_status_code, 400)

                # test anything else
                deed_model.status = "Foo"
                mock_get_deed.return_value = deed_model
                response_status_code = make_effective(123)[1]
                mock_jsonify.assert_called_with(
                    {'errors':
                        ['Problem 1: This deed cannot be made effective as not all borrowers have signed the deed.']})
                self.assertEqual(response_status_code, 400)

    @mock.patch('json.dumps')
    def test_check_health(self, mock_status):
        mock_status.side_effect = EsecException
        response = self.app.get('/health')
        self.assertEqual(response.data, b'')
        self.assertEqual(response.status_code, 200)

    @mock.patch('application.deed.views.jsonify')
    @mock.patch('application.deed.model.Deed.get_signed_deeds')
    def test_retrieve_signed_deeds(self, mock_get_status, mock_jsonify):
        mock_get_status.return_value = ["signeddeed1", "signeddeed2"]
        retrieve_signed_deed()
        mock_jsonify.assert_called_with({"deeds": ["signeddeed1", "signeddeed2"]})

    @mock.patch('application.deed.views.jsonify')
    @mock.patch('application.deed.model.Deed.get_signed_deeds')
    def test_retrieve_signed_deeds_none_found(self, mock_get_status, mock_jsonify):
        mock_get_status.return_value = []
        retrieve_signed_deed()
        mock_jsonify.assert_called_with({"message": "There are no deeds which have been fully signed"})


class TestGetDeed(TestRoutesBase):

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_endpoint(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()
        headers = self.webseal_headers.copy()
        headers["Accept"] = 'application/json'
        response = self.app.get(self.DEED_ENDPOINT + 'AB1234',
                                headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("DN100" in response.data.decode())

    @mock.patch('application.deed.model.Deed.get_deed_status', autospec=True)
    def test_get_no_status_with_mdref_and_titleno_endpoint_no_status(self, get_deed_status):
        get_deed_status.return_value = StatusMock()._no_status_with_mdref_and_titleno

        response = self.app.get(self.DEED_QUERY + '?md_ref=e-MD12344&title_number=DN100')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_endpoint_no_specified_accept_type(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()
        response = self.app.get(self.DEED_ENDPOINT + 'AB1234',
                                headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("DN100" in response.data.decode())

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_endpoint_pdf_content_type(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()
        headers = self.webseal_headers.copy()
        headers["Accept"] = 'application/pdf'
        response = self.app.get(self.DEED_ENDPOINT + 'AB1234',
                                headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = PyPDF2.PdfFileReader(io.BytesIO(response.data))
        txt = obj.getPage(0).extractText()
        self.assertTrue('Digital Mortgage Deed' in txt)
        self.assertTrue('e-MD12344' in txt)


class TestRoutesErrorHandlers(TestRoutesBase):

    @mock.patch('application.service_clients.esec.implementation._post_request')
    def test_esec_down_gives_200(self, mock_request):
        with app.app_context() as ac:
            def fake_post(url, data):
                return FakeResponse(content='Foo')

            ac.g.trace_id = None

            # Mock out the actual call to the _post_request and return an error
            mock_request.side_effect = requests.ConnectionError

            self.assertRaises(EsecException, sign_document_with_authority, "Foo")

    @mock.patch('application.deed.model.Deed.get_deed')
    def test_file_not_found_exception(self, mock_get_deed):
        mock_get_deed.return_value = None

        response = self.app.get(self.DEED_ENDPOINT + 'AB1234',
                                headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        def test_borrower_token(self):
            token = Borrower.generate_token()
            char_list = ['I', 'O', 'W', 'Z']
            res = False

            if any((c in char_list) for c in token):
                res = True

            self.assertTrue(token.isupper())
            self.assertFalse(res)


class TestValidators(TestRoutesBase):
    def test_validation_order(self):
        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                obj = Validation()
                result, msg = obj.validate_dob(DeedHelper._json_doc_future_dob)

                self.assertFalse(result)

                result, msg = obj.validate_phonenumbers(DeedHelper._borrowers_with_same_phonenumber)

                self.assertFalse(result)


class TestCreateDeed(TestRoutesBase):
    @mock.patch('application.mortgage_document.model.MortgageDocument.query', autospec=True)
    @mock.patch('application.deed.views.Validation.validate_phonenumbers')
    @mock.patch('application.deed.views.Validation.validate_dob')
    @mock.patch('application.deed.views.Validation.call_akuma')
    @mock.patch('application.deed.views.Validation.validate_borrower_names')
    @mock.patch('application.deed.views.Validation.validate_title_number')
    @mock.patch('application.deed.views.Validation.validate_payload')
    @mock.patch('application.deed.views.update_deed')
    @mock.patch('application.deed.views.Validation.validate_organisation_credentials')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_get_existing_deed_and_update(self, mock_deed, mock_org_cred, mock_update, mock_val_payload, mock_val_tn,
                                          mock_val_bor, mock_akuma, mock_val_dob, mock_val_phone, mock_query):

        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = MortgageDocMock()
        mock_val_payload.return_value = None
        mock_val_tn.return_value = "title OK"
        mock_val_bor.return_value = True, ""
        mock_val_dob.return_value = True, ""
        mock_val_phone.return_value = True, ""
        mock_akuma.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }
        mock_deed.return_value = DeedModelMock()
        mock_update.return_value = True, "OK"

        payload = json.dumps(DeedHelper._json_doc_update)
        response = self.app.put(self.DEED_ENDPOINT + 'AAAAAA', data=payload,
                                headers=self.webseal_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('application.deed.views.Validation.validate_phonenumbers')
    @mock.patch('application.deed.views.Validation.validate_dob')
    @mock.patch('application.deed.views.Validation.call_akuma')
    @mock.patch('application.deed.views.Validation.validate_borrower_names')
    @mock.patch('application.deed.views.Validation.validate_title_number')
    @mock.patch('application.deed.views.Validation.validate_payload')
    @mock.patch('application.deed.views.update_deed')
    @mock.patch('application.deed.views.Validation.validate_organisation_credentials')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_get_existing_deed_and_update_bad_payload(self, mock_deed, mock_org_cred, mock_update, mock_val_payload,
                                                      mock_val_tn, mock_val_bor, mock_akuma, mock_val_dob,
                                                      mock_val_phone):
        # test validate_payload
        mock_val_payload.return_value = 1, "Foo"
        mock_val_tn.return_value = "OK"
        mock_val_bor.return_value = True, ""
        mock_val_dob.return_value = True, ""
        mock_val_phone.return_value = True, ""

        mock_deed.return_value = DeedModelMock()
        mock_update.return_value = True, "OK"
        payload = json.dumps(DeedHelper._json_doc_update)

        response = self.app.put(self.DEED_ENDPOINT + 'AAAAAA', data=payload,
                                headers=self.webseal_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.deed.views.Validation.validate_phonenumbers')
    @mock.patch('application.deed.views.Validation.validate_dob')
    @mock.patch('application.deed.views.Validation.call_akuma')
    @mock.patch('application.deed.views.Validation.validate_borrower_names')
    @mock.patch('application.deed.views.Validation.validate_title_number')
    @mock.patch('application.deed.views.Validation.validate_payload')
    @mock.patch('application.deed.views.update_deed')
    @mock.patch('application.deed.views.Validation.validate_organisation_credentials')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_get_existing_deed_and_update_bad_title(self, mock_deed, mock_org_cred, mock_update, mock_val_payload,
                                                    mock_val_tn, mock_val_bor, mock_akuma, mock_val_dob,
                                                    mock_val_phone):
        # test validate_title_number
        mock_val_payload.return_value = 0, "No error message"
        mock_val_tn.return_value = "Title does not exist."
        mock_val_bor.return_value = True, ""
        mock_val_dob.return_value = True, ""
        mock_val_phone.return_value = True, ""

        mock_deed.return_value = DeedModelMock()
        mock_update.return_value = True, "OK"

        payload = json.dumps(DeedHelper._json_doc_update)
        response = self.app.put(self.DEED_ENDPOINT + 'AAAAAA', data=payload,
                                headers=self.webseal_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.deed.views.Validation.validate_phonenumbers')
    @mock.patch('application.deed.views.Validation.validate_dob')
    @mock.patch('application.deed.views.Validation.call_akuma')
    @mock.patch('application.deed.views.Validation.validate_borrower_names')
    @mock.patch('application.deed.views.Validation.validate_title_number')
    @mock.patch('application.deed.views.Validation.validate_payload')
    @mock.patch('application.deed.views.update_deed')
    @mock.patch('application.deed.views.Validation.validate_organisation_credentials')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_get_existing_deed_and_update_bad_borrowers(self, mock_deed, mock_org_cred, mock_update, mock_val_payload,
                                                        mock_val_tn, mock_val_bor, mock_akuma, mock_val_dob,
                                                        mock_val_phone):
        # test validate_borrower_names
        mock_val_payload.return_value = 0, "No error message"
        mock_val_tn.return_value = "OK"
        mock_val_bor.return_value = False, "fail"
        mock_val_dob.return_value = True, ""
        mock_val_phone.return_value = True, ""

        mock_deed.return_value = DeedModelMock()
        mock_update.return_value = True, "OK"

        payload = json.dumps(DeedHelper._json_doc_update)
        response = self.app.put(self.DEED_ENDPOINT + 'AAAAAA', data=payload,
                                headers=self.webseal_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.deed.views.Validation.validate_phonenumbers')
    @mock.patch('application.deed.views.Validation.validate_dob')
    @mock.patch('application.deed.views.Validation.call_akuma')
    @mock.patch('application.deed.views.Validation.validate_borrower_names')
    @mock.patch('application.deed.views.Validation.validate_title_number')
    @mock.patch('application.deed.views.Validation.validate_payload')
    @mock.patch('application.deed.views.update_deed')
    @mock.patch('application.deed.views.Validation.validate_organisation_credentials')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_get_existing_deed_and_update_bad_dob(self, mock_deed, mock_org_cred, mock_update, mock_val_payload,
                                                  mock_val_tn, mock_val_bor, mock_akuma, mock_val_dob, mock_val_phone):
        # test validate_dob
        mock_val_payload.return_value = 0, "No error message"
        mock_val_tn.return_value = "OK"
        mock_val_bor.return_value = True, ""
        mock_val_dob.return_value = False, "fail"

        mock_deed.return_value = DeedModelMock()
        mock_update.return_value = True, "OK"

        payload = json.dumps(DeedHelper._json_doc_update)
        response = self.app.put(self.DEED_ENDPOINT + 'AAAAAA', data=payload,
                                headers=self.webseal_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.deed.views.Validation.validate_phonenumbers')
    @mock.patch('application.deed.views.Validation.validate_dob')
    @mock.patch('application.deed.views.Validation.call_akuma')
    @mock.patch('application.deed.views.Validation.validate_borrower_names')
    @mock.patch('application.deed.views.Validation.validate_title_number')
    @mock.patch('application.deed.views.Validation.validate_payload')
    @mock.patch('application.deed.views.update_deed')
    @mock.patch('application.deed.views.Validation.validate_organisation_credentials')
    @mock.patch('application.deed.views.Deed.get_deed')
    def test_get_existing_deed_and_update_bad_phone_numbers(self, mock_deed, mock_org_cred, mock_update,
                                                            mock_val_payload, mock_val_tn, mock_val_bor, mock_akuma,
                                                            mock_val_dob, mock_val_phone):

        # test validate_phonenumbers
        mock_val_payload.return_value = 0, "No error message"
        mock_val_tn.return_value = "OK"
        mock_val_bor.return_value = True, ""
        mock_val_dob.return_value = True, ""
        mock_val_phone.return_value = False, "fail"

        mock_deed.return_value = DeedModelMock()
        mock_update.return_value = True, "OK"

        payload = json.dumps(DeedHelper._json_doc_update)
        response = self.app.put(self.DEED_ENDPOINT + 'AAAAAA', data=payload,
                                headers=self.webseal_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUpdateDeed(TestRoutesBase):

    @mock.patch('application.borrower.model.Borrower._delete_borrower')
    @mock.patch('application.borrower.model.Borrower._get_borrowers_not_on_deed')
    def test_delete_borrowers_not_on_deed(self, mock_get_borrowers, mock_delete):
        delete_borrowers = Borrower()
        res = delete_borrowers.delete_borrowers_not_on_deed([1, 2], "AAAAA")

        self.assertTrue(res)

    @mock.patch('application.borrower.model.Borrower._delete_borrower')
    @mock.patch('application.borrower.model.Borrower._get_borrowers_not_on_deed')
    def test_delete_borrowers_not_on_deed_fail(self, mock_get_borrowers, mock_delete):
        mock_get_borrowers.side_effect = DatabaseException('BOOM')
        delete_borrowers = Borrower()

        self.assertRaises(DatabaseException, delete_borrowers.delete_borrowers_not_on_deed, [1, 2], "AAAAA")

    @mock.patch('application.service_clients.organisation_adapter.implementation._get_request')
    def test_get_organisation_name(self, mock_organisation_name):

        with app.app_context() as ac:
            ac.g.trace_id = None
            with app.test_request_context():
                #  A test to check that the logic contained within the get_organisation_name method
                #  returns a "not found" if the call to get the name matches no organisation, or
                #  the name, if it does match.
                mock_organisation_name.return_value = "not found"
                organisation_name = get_organisation_name("1000.1.2", "Test Organisation")

                self.assertEqual(organisation_name, "Test Organisation")

                mock_organisation_name.return_value = "Test Organisation"
                organisation_name = get_organisation_name("1000.1.2", "Test [22022] Organisation")

                self.assertEqual(organisation_name, "Test Organisation")
