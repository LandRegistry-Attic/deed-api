import PyPDF2
import copy
import io
import os
import json
import requests
import unittest
import time
from application.deed.model import Deed
from integration_tests.deed.deed_data import valid_deed, new_deed, valid_deed_with_reference, \
    valid_deed_with_date_of_mortgage_offer, valid_deed_with_miscellaneous_info
from lxml import etree

from application import config
from integration_tests.helper import setUpApp, setUp_MortgageDocuments

import datetime


class TestDeedRoutes(unittest.TestCase):
    webseal_headers = {
        "Content-Type": "application/json",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv('WEBSEAL_HEADER_VALUE')
    }

    webseal_headers_2 = {
        "Content-Type": "application/json",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv("WEBSEAL_HEADER_INT_TEST_2")
    }

    webseal_test_headers3 = {
        "Content-Type": "application/json",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv("WEBSEAL_HEADER_INT_TEST_3")
    }

    webseal_headers_internal = {
        "Content-Type": "application/json",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv("WEBSEAL_HEADER_INT_INTERNAL")
    }

    webseal_headers_for_pdf = {
        "Content-Type": "application/json",
        "Accept": "application/pdf",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv('WEBSEAL_HEADER_VALUE')
    }

    webseal_test_organisation_name = {
        "Content-Type": "application/json",
        "Accept": "application/pdf",
        os.getenv("WEBSEAL_HEADER_KEY"): os.getenv("WEBSEAL_HEADER_INT_ORGANISATION")
    }

    def setUp(self):
        setUpApp(self)
        setUp_MortgageDocuments(self)

    def deed_create_and_get(self, deed):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(deed),
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
        if 'reference' in deed:
            self.assertIn("reference", str(created_deed['deed']))
            self.assertEqual(deed['reference'],
                             str(created_deed['deed']['reference_details']['lender_reference_value']))

    def test_deed_create_and_get(self):
        self.deed_create_and_get(valid_deed)

    def test_deed_create_and_get_with_optional_reference(self):
        self.deed_create_and_get(valid_deed_with_reference)

    def test_deed_create_and_get_with_optional_date_of_mortgage_offer(self):
        self.deed_create_and_get(valid_deed_with_date_of_mortgage_offer)

    def test_deed_create_and_get_with_optional_miscellaneous_info(self):
        self.deed_create_and_get(valid_deed_with_miscellaneous_info)

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

    def deed_internal_create_and_get(self, deed):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        self.assertIn("/deed/", str(response_json))

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"] + '/internal')
        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()
        self.assertIn("deed", str(created_deed))

    def test_deed_internal_create_and_get(self):
        self.deed_internal_create_and_get(valid_deed)

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
                                                  "dob": "02/02/1922"}),
                                 headers=self.webseal_headers)

        self.assertEqual(response.status_code, 200)

    def test_validate_borrower_not_found(self):
        response = requests.post(config.DEED_API_BASE_HOST + '/borrower/validate',
                                 data=json.dumps({"borrower_token": "unknown",
                                                  "dob": "02/02/1922"}),
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
                                        headers=self.webseal_headers)
        self.assertEqual(get_created_deed.status_code, 200)

    def test_save_make_effective(self):
        get_existing_deeds = requests.get(config.DEED_API_BASE_HOST + '/deed/retrieve-signed',
                                          headers=self.webseal_headers)

        get_existing_deeds = get_existing_deeds.json()

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

        get_deed_again = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                      headers=self.webseal_headers)

        second_deed = get_deed_again.json()

        timer = time.time() + 15
        while time.time() < timer or second_deed["deed"]["status"] != "ALL-SIGNED":
            get_deed_again = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                          headers=self.webseal_headers)

            second_deed = get_deed_again.json()

        test_result = requests.get(config.DEED_API_BASE_HOST + '/deed/retrieve-signed',
                                   headers=self.webseal_headers)

        test_result = test_result.json()

        self.assertGreater(len(test_result["deeds"]), len(get_existing_deeds["deeds"]))

        make_effective = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/make-effective',
                                       headers=self.webseal_headers)

        self.assertEqual(make_effective.status_code, 200)

        deed_model = Deed()

        result = deed_model.get_deed_system(response_json["path"].replace("/deed/", ""))

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

        get_deed_again = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                      headers=self.webseal_headers)

        second_deed = get_deed_again.json()

        timer = time.time() + 15
        while time.time() < timer or second_deed["deed"]["status"] != "ALL-SIGNED":
            get_deed_again = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                          headers=self.webseal_headers)

            second_deed = get_deed_again.json()

        test_result = requests.get(config.DEED_API_BASE_HOST + '/deed/retrieve-signed',
                                   headers=self.webseal_headers)

        signed_deeds = test_result.json()
        self.assertIn("deeds", str(signed_deeds))
        self.assertIn(created_deed["deed"]["token"], str(signed_deeds))

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
                                    data=json.dumps(valid_deed_with_reference),
                                    headers=self.webseal_headers)
        response_json = create_deed.json()
        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers_for_pdf)
        obj = PyPDF2.PdfFileReader(io.BytesIO(get_created_deed.content))
        txt = obj.getPage(0).extractText()
        self.assertTrue('Digital Mortgage Deed' in txt)
        txt = obj.getPage(1).extractText()
        self.assertTrue(valid_deed_with_reference['md_ref'] in txt)
        self.assertTrue(valid_deed_with_reference['reference'] in txt)
        # Can look at this file if you want.
        f = open('integration_test_deed.pdf', 'wb')
        f.write(get_created_deed.content)
        f.close()

    def test_modify_existing_deed(self):
        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)

        self.assertEqual(create_deed.status_code, 201)
        response_json = create_deed.json()
        self.assertIn("/deed/", str(response_json))
        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=self.webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        modify_deed = requests.put(config.DEED_API_BASE_HOST + response_json["path"],
                                   data=json.dumps(new_deed),
                                   headers=self.webseal_headers)

        modify_response_json = modify_deed.json()
        self.assertIn("/deed/", str(modify_response_json))
        get_modified_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                         headers=self.webseal_headers)

        self.assertEqual(get_modified_deed.status_code, 200)
        modified_deed = get_modified_deed.json()
        self.assertEqual(modified_deed["deed"]["property_address"], "0 The Drive, This Town, This County, PL0 0TH")

    def test_accept_naa(self):
        res = requests.post(config.DEED_API_BASE_HOST + '/naa/accept/1',
                            headers=self.webseal_headers)

        response_json = res.json()

        get = requests.get(config.DEED_API_BASE_HOST + '/naa/accept/' + str(response_json["id"]),
                           headers=self.webseal_headers)
        return_value = get.json()
        self.assertEqual(return_value["borrower_id"], 1)

    def test_organisation_name(self):
        try:
            # Post a new test organisation, which will match the one provided in the test headers
            post_organisation_name = requests.post(config.ORGANISATION_API_BASE_HOST + '/organisation-name',
                                                   data=json.dumps({"organisation_name": "Test Organisation", "legal_organisation_name": "Legal Organisation"}),
                                                   headers=self.webseal_test_organisation_name)

            self.assertEqual(post_organisation_name.status_code, 201)

            # Create a new test deed and attempt to retrieve the organisation name from it
            # which should match the posted organisation above
            create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                        data=json.dumps(valid_deed),
                                        headers=self.webseal_test_organisation_name)
            self.assertEqual(create_deed.status_code, 201)
            response_json = create_deed.json()
            self.assertIn("/deed/", str(response_json))

            get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                            headers=self.webseal_test_organisation_name)

            self.assertEqual(get_created_deed.status_code, 200)

            get_organisation_name = requests.get(
                config.DEED_API_BASE_HOST + response_json["path"] + '/organisation-name',
                headers=self.webseal_test_organisation_name)
            self.assertEqual(get_organisation_name.status_code, 200)
            self.assertEqual(get_organisation_name.json()['result'], 'Legal Organisation')

        finally:
            # Finally, teardown/delete the test organisation name
            delete_organisation_name = requests.delete(
                config.ORGANISATION_API_BASE_HOST + '/organisation-name/Test Organisation')

            self.assertEqual(delete_organisation_name.status_code, 200)

    def test_additional_columns(self):

        our_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/', data=json.dumps(valid_deed), headers=self.webseal_headers)

        response_json = our_deed.json()

        response_path = response_json['path'].replace('/deed/', '')

        create_deed = Deed()

        deed_returned = create_deed.get_deed_system(response_path)

        self.assertIsInstance(deed_returned.created_date, datetime.datetime)
        self.assertEqual(deed_returned.payload_json, valid_deed)
