import json
import io
import unittest
import copy

import requests
import PyPDF2

from integration_tests.helper import setUpApp, setUp_MortgageDocuments
from integration_tests.deed.deed_data import valid_deed
from application import config
from application.deed.model import Deed
from lxml import etree


class TestDeedRoutes(unittest.TestCase):
    webseal_headers = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Devices,O=1359.2.1,C=gb"
    }

    webseal_headers_2 = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Test,O=1360,C=gb"
    }

    webseal_test_headers3 = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20TestD,O=1362.5.1,C=gb"
    }

    webseal_headers_internal = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Test2,O=*,C=gb"
    }

    webseal_headers_for_pdf = {
        "Content-Type": "application/json",
        "Accept": "application/pdf",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Devices,O=1359.2.1,C=gb"
    }

    def setUp(self):
        setUpApp(self)
        setUp_MortgageDocuments(self)

    def test_deed_create_and_get(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        self.assertIn("/deed/", str(response_json))

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers)
        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()

        self.assertIn("title_number", str(created_deed['deed']))
        self.assertIn("borrowers", str(created_deed['deed']))
        self.assertIn("forename", str(created_deed['deed']))
        self.assertIn("surname", str(created_deed['deed']))
        self.assertIn("charge_clause", str(created_deed['deed']))
        self.assertIn("additional_provisions", str(created_deed['deed']))
        self.assertIn("lender", str(created_deed['deed']))
        self.assertIn("property_address", str(created_deed['deed']))

    def test_bad_get(self):
        fake_token_deed = requests.get(config.DEED_API_BASE_HOST + "/deed/fake",
                                       headers=self.webseal_headers)
        self.assertEqual(fake_token_deed.status_code, 404)

    def test_deed_create_and_get_by_mdref_and_titleno(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        self.assertIn("/deed/", str(response_json))

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + "/deed?md_ref=" + valid_deed["md_ref"] +
                                        "&title_number=" + valid_deed["title_number"],
                                        headers=self.webseal_headers)
        self.assertEqual(get_created_deed.status_code, 200)

        get_deed_data = get_created_deed.json()

        self.assertIn("token", str(get_deed_data))
        self.assertIn("status", str(get_deed_data))
        self.assertIn("DRAFT", str(get_deed_data))
        self.assertIn(response_json["path"][-6:], str(get_deed_data))

    def test_invalid_params_on_get_with_mdref_and_titleno(self):
        fake_token_deed = requests.get(config.DEED_API_BASE_HOST + "/deed?invalid_query_parameter=invalid",
                                       headers=self.webseal_headers)

        self.assertEqual(fake_token_deed.status_code, 400)

    def test_invalid_query_params_on_get_with_mdref_and_titleno(self):
        fake_token_deed = requests.get(config.DEED_API_BASE_HOST + "/deed?md_ref=InvalidMD&title_number=InvalidTitleNo",
                                       headers=self.webseal_headers)

        self.assertEqual(fake_token_deed.status_code, 404)

    def test_deed_without_borrowers(self):
        deed_without_borrowers = copy.deepcopy(valid_deed)
        deed_without_borrowers["borrowers"] = []

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(deed_without_borrowers),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 400)

    def test_deed_without_title(self):
        deed_without_title_number = copy.deepcopy(valid_deed)
        del deed_without_title_number["title_number"]

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(deed_without_title_number),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 400)

    def test_deed_with_missing_borrower_properties(self):
        deed_with_invalid_borrower = copy.deepcopy(valid_deed)
        deed_with_invalid_borrower["borrowers"] = [
            {
                "forename": "lisa"
            }
        ]

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(deed_with_invalid_borrower),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 400)

    def test_deed_without_md_ref(self):
        deed_without_md_ref = copy.deepcopy(valid_deed)
        del deed_without_md_ref["md_ref"]

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(deed_without_md_ref),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 400)

    def test_deed_without_address(self):
        deed_without_address = copy.deepcopy(valid_deed)
        del deed_without_address["property_address"]

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(deed_without_address),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 400)

    def test_deed_with_unknown_md_ref(self):
        deed_with_unknown_md_ref = copy.deepcopy(valid_deed)
        deed_with_unknown_md_ref["md_ref"] = "e-MD111G"

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(deed_with_unknown_md_ref),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 400)

    def test_delete_borrower(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        borrower = get_created_deed.json()

        response = requests.delete(
            config.DEED_API_BASE_HOST + '/deed/borrowers/delete/' + str(borrower["deed"]["borrowers"][0]["id"]))

        self.assertEqual(response.status_code, 200)

    def test_delete_borrower_none_exists(self):
        response = requests.delete(config.DEED_API_BASE_HOST + '/deed/borrowers/delete/999999999')

        self.assertEqual(response.status_code, 404)

    def test_validate_borrower(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        borrower = get_created_deed.json()

        response = requests.post(config.DEED_API_BASE_HOST + '/borrower/validate',
                                 data=json.dumps({"borrower_token": borrower["deed"]["borrowers"][0]["token"],
                                                  "dob": "23/01/1986"}),
                                 headers=self.webseal_headers)

        self.assertEqual(response.status_code, 200)

    def test_validate_borrower_not_found(self):
        response = requests.post(config.DEED_API_BASE_HOST + '/borrower/validate',
                                 data=json.dumps({"borrower_token": "unknown",
                                                  "dob": "23/01/1986"}),
                                 headers=self.webseal_headers)
        self.assertEqual(response.status_code, 404)

    def test_deed_create_and_get_diff_org(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        self.assertIn("/deed/", str(response_json))

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers_2)
        self.assertEqual(get_created_deed.status_code, 404)

        response_json = create_deed.json()
        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers_internal)
        self.assertEqual(get_created_deed.status_code, 200)

    def test_save_make_effective(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()

        code_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"]
        }

        request_code = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/request-auth-code',
                                     data=json.dumps(code_payload),
                                     headers=self.webseal_headers)

        self.assertEqual(request_code.status_code, 200)

        sign_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"],
            "authentication_code": "aaaa"
        }

        sign_deed = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/verify-auth-code',
                                  data=json.dumps(sign_payload),
                                  headers=self.webseal_headers)

        self.assertEqual(sign_deed.status_code, 200)

        make_effective = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/make-effective',
                                       headers=self.webseal_headers)

        self.assertEqual(make_effective.status_code, 200)

        deed_model = Deed()

        result = deed_model._get_deed_internal(response_json["path"].replace("/deed/", ""), "*")

        self.assertIsNotNone(result.deed_xml)

        mock_xml = etree.fromstring(result.deed_xml)
        for val in mock_xml.xpath("/dm-application/effectiveDate"):
            test_result = val.text

        self.assertIsNotNone(test_result)

    def test_get_signed_deeds(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()

        code_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"]
        }

        request_code = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/request-auth-code',
                                     data=json.dumps(code_payload),
                                     headers=self.webseal_headers)

        self.assertEqual(request_code.status_code, 200)

        sign_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"],
            "authentication_code": "aaaa"
        }

        sign_deed = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/verify-auth-code',
                                  data=json.dumps(sign_payload),
                                  headers=self.webseal_headers)

        self.assertEqual(sign_deed.status_code, 200)

        test_result = requests.get(config.DEED_API_BASE_HOST + '/deed/retrieve-signed',
                                   headers=self.webseal_headers)

        signed_deeds = test_result.json()
        self.assertIn("deeds", str(signed_deeds))

    def test_get_signed_deeds_not_found(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()

        code_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"]
        }

        request_code = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/request-auth-code',
                                     data=json.dumps(code_payload),
                                     headers=self.webseal_headers)

        self.assertEqual(request_code.status_code, 200)

        sign_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"],
            "authentication_code": "aaaa"
        }

        sign_deed = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/verify-auth-code',
                                  data=json.dumps(sign_payload),
                                  headers=self.webseal_headers)

        self.assertEqual(sign_deed.status_code, 200)

        test_result = requests.get(config.DEED_API_BASE_HOST + '/deed/retrieve-signed',
                                   headers=self.webseal_test_headers3)

        self.assertEqual(test_result.status_code, 404)

    def test_deed_pdf(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        response_json = create_deed.json()
        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers_for_pdf)
        obj = PyPDF2.PdfFileReader(io.BytesIO(get_created_deed.content))
        txt = obj.getPage(0).extractText()
        self.assertTrue('Digital Mortgage Deed' in txt)
        txt = obj.getPage(1).extractText()
        self.assertTrue('e-MD12344' in txt)
        # Can look at this file if you want.
        f = open('integration_test_deed.pdf', 'wb')
        f.write(get_created_deed.content)
        f.close()
