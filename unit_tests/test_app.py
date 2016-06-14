from application import app
from application.deed.model import Deed
from application.casework.service import get_document
from unit_tests.helper import DeedHelper, DeedModelMock, MortgageDocMock, StatusMock
from application.akuma.service import Akuma
from application.deed.utils import convert_json_to_xml, validate_generated_xml
from application.deed.service import make_effective_text, make_deed_effective_date
from application.deed.views import make_effective
from flask.ext.api import status
from unit_tests.schema_tests import run_schema_checks
from application.borrower.model import generate_hex
import unittest
import json
import mock
from application.borrower.model import Borrower
from datetime import datetime


class TestRoutes(unittest.TestCase):
    DEED_ENDPOINT = "/deed/"
    DEED_QUERY = "/deed"
    BORROWER_ENDPOINT = "/borrower/"
    CASEWORK_ENDPOINT = "/casework/"

    non_webseal_headers = {
        "Content-Type": "application/json"
    }
    webseal_headers = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Devices,O=1359.2.1,C=gb"
    }
    dodgy_webseal_headers1 = {
        "Content-Type": "application/json",
        "Iv-User-L": "incorrect data"
    }

    def setUp(self):
        app.config.from_pyfile("config.py")
        self.app = app.test_client()

    def test_health(self):
        self.assertEqual((self.app.get('/health')).status_code,
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

    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.mortgage_document.model.MortgageDocument.query', autospec=True)
    def test_create_no_auth_headers(self, mock_query, mock_Deed, mock_Borrower, mock_akuma, mock_proprietor_names):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = MortgageDocMock()
        mock_akuma.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }
        mock_proprietor_names.return_value = ['lisa ann bloggette', 'frank ann bloggette']
        payload = json.dumps(DeedHelper._json_doc)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.title_adaptor.service.TitleAdaptor.do_check', autospec=False)
    @mock.patch('application.service_clients.akuma.interface.AkumaInterface.perform_check')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    @mock.patch('application.mortgage_document.model.MortgageDocument.query', autospec=True)
    def test_create_webseal_external(self, mock_query, mock_Deed, mock_Borrower, mock_akuma, mock_title, mock_proprietor_names):
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

    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    def test_create_with_invalid(self, mock_Borrower, mock_Deed, mock_proprietor_names):
        mock_proprietor_names.return_value = ['lisa bloggette', 'frank bloggette']
        payload = json.dumps(DeedHelper._invalid_phone_numbers)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    def test_create_with_invalid_blanks(self, mock_Borrower, mock_Deed, mock_proprietor_names):
        payload = json.dumps(DeedHelper._invalid_blanks_on_required_fields)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    def test_invalid_title_format(self, mock_proprietor_names):
        payload = json.dumps(DeedHelper._invalid_title)
        response = self.app.post(self.DEED_ENDPOINT, data=payload,
                                 headers={"Content-Type": "application/json"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_endpoint(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()

        response = self.app.get(self.DEED_ENDPOINT + 'AB1234',
                                headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("DN100" in response.data.decode())

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

    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_get_endpoint_not_found(self, mock_query):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = None

        response = self.app.get(self.DEED_ENDPOINT + 'CD3456',
                                headers=self.webseal_headers)
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
            deed_token = "aaaaaa"
            dob = "23/01/1986"
            phonenumber = "07502154999"

        mock_borrower.return_value = ReturnedBorrower()
        payload = json.dumps(DeedHelper._validate_borrower)
        response = self.app.post(self.BORROWER_ENDPOINT + "validate",
                                 data=payload,
                                 headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('application.borrower.model.Borrower.get_by_token')
    def test_validate_borrower_no_leading_zero(self, mock_borrower):
        class ReturnedBorrower:
            deed_token = "aaaaaa"
            dob = "01/01/1986"
            phonenumber = "07502154999"

        mock_borrower.return_value = ReturnedBorrower()
        payload = json.dumps(DeedHelper._validate_borrower_dob)
        response = self.app.post(self.BORROWER_ENDPOINT + "validate",
                                 data=payload,
                                 headers={"Content-Type": "application/json"})
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

    @mock.patch('application.service_clients.register_adapter.interface.RegisterAdapterInterface.get_proprietor_names')
    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.deed.model.Deed.save')
    def test_create_with_invalid_address(self, mock_Borrower, mock_Deed, mock_proprietor_names):
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
    def test_akuma_check(self, mock_api):
        mock_api.return_value = {
            "result": "A",
            "id": "2b9115b2-d956-11e5-942f-08002719cd16"
        }

        check_result = Akuma.do_check(DeedHelper._json_doc, "create deed", "Land Registry Devices", "gb")

        self.assertEqual(check_result["result"], "A")

    def test_make_effective_clause(self):

        effective_clause = make_effective_text("Test Organisation")
        correct_effective_clause = "This charge takes effect when the registrar receives notification from " + \
                                   "Test Organisation that the charge is to take effect."

        self.assertEqual(effective_clause, correct_effective_clause)

    def test_uuid_generation(self):
        a = {}
        for f in range(0, 100000):
            new_hash = generate_hex()
            a[new_hash] = True

        self.assertEqual(100000, len(a))

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
            dob = "01/01/1986"
            forename = "Jack"
            surname = "Jones"

        mock_borrower.return_value = ReturnedBorrower()
        mock_borrower_save.return_value = "OK"

        payload = json.dumps(DeedHelper._add_borrower_signature)

        response = self.app.post(self.DEED_ENDPOINT + 'AB1234' + '/request-auth-code',
                                 data=payload,
                                 headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('application.borrower.model.Borrower.get_by_token')
    @mock.patch('application.service_clients.esec.interface.EsecClientInterface.reissue_sms')
    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_reissue_auth_code(self, mock_query, mock_reissue, mock_borrower):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()
        mock_reissue.return_value = "SUCCESS", 200

        class ReturnedBorrower(Borrower):
            deed_token = "aaaaaa"
            dob = "01/01/1986"
            forename = "Jack"
            surname = "Jones"
            esec_user_name = "DM123"

        mock_borrower.return_value = ReturnedBorrower()

        payload = json.dumps(DeedHelper._add_borrower_signature)

        response = self.app.post(self.DEED_ENDPOINT + 'AB1234' + '/request-auth-code',
                                 data=payload,
                                 headers=self.webseal_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('application.borrower.model.Borrower.save')
    @mock.patch('application.borrower.model.Borrower.get_by_token')
    @mock.patch('application.deed.utils.get_borrower_position')
    @mock.patch('application.service_clients.esec.interface.EsecClientInterface.auth_sms')
    @mock.patch('application.deed.model.Deed.save', autospec=True)
    @mock.patch('application.deed.model.Deed.query', autospec=True)
    def test_add_authenticate_and_sign(self, mock_query, mock_Deed_save,
                                       mock_auth, mock_position, mock_borrower, mock_borrower_save):
        mock_instance_response = mock_query.filter_by.return_value
        mock_instance_response.first.return_value = DeedModelMock()

        class ReturnedBorrower(Borrower):
            deed_token = "aaaaaa"
            dob = "01/01/1986"
            forename = "Jack"
            surname = "Jones"
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

    def test_global_exception_handler(self):
        self.assertEqual((self.app.get('/div_zero')).status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual((self.app.get('/div_zero')).status,
                         '500 INTERNAL SERVER ERROR')
        self.assertEqual((self.app.get('/div_zero').data),
                         b'{\n  "message": "Unexpected error."\n}')

    @mock.patch('application.deed.model.Deed.get_deed')
    @mock.patch('application.deed.views.abort')
    def test_make_deed_effective_404(self, mock_abort, mock_get_deed):
        mock_get_deed.return_value = None
        make_effective(123)
        mock_abort.assert_called_with(status.HTTP_404_NOT_FOUND)

    @mock.patch('application.deed.model.Deed.get_deed')
    @mock.patch('application.deed.views.Akuma.do_check')
    @mock.patch('application.deed.views.jsonify')
    @mock.patch('application.deed.views.datetime')
    def test_make_deed_effective_200(self, mock_datetime, mock_jsonify, mock_akuma,
                                     mock_get_deed):
        deed_model = mock.create_autospec(Deed)
        deed_model.deed = {}
        deed_model.status = "ALL-SIGNED"
        mock_datetime.now.return_value = datetime(1900, 1, 1)
        mock_get_deed.return_value = deed_model
        response_status_code = make_effective(123)[1]
        mock_jsonify.assert_called_with({'deed': {'effective_date': '1900-01-01 00:00:00'}})
        self.assertEqual(response_status_code, 200)

    @mock.patch('application.deed.model.Deed.get_deed')
    @mock.patch('application.deed.views.Akuma.do_check')
    @mock.patch('application.deed.views.jsonify')
    def test_make_deed_effective_400(self, mock_jsonify, mock_akuma, mock_get_deed):
        deed_model = mock.create_autospec(Deed)
        deed_model.deed = {}

        # test where already effective
        deed_model.status = "EFFECTIVE"
        mock_get_deed.return_value = deed_model
        response_status_code = make_effective(123)[1]
        mock_jsonify.assert_called_with({"message": "This deed has already been made effective."})
        self.assertEqual(response_status_code, 400)

        # test where not registrar signed
        deed_model.status = "NOT-LR-SIGNED"
        mock_get_deed.return_value = deed_model
        response_status_code = make_effective(123)[1]
        mock_jsonify.assert_called_with({"message": "This deed has already been made effective."})
        self.assertEqual(response_status_code, 400)

        # test anything else
        deed_model.status = "Foo"
        mock_get_deed.return_value = deed_model
        response_status_code = make_effective(123)[1]
        mock_jsonify.assert_called_with({"message": "You can not make this deed effective as it is not "
                                                    "fully signed"})
        self.assertEqual(response_status_code, 400)


