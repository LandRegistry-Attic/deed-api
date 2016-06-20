import json
import unittest
from integration_tests.helper import setUpApp, setUpDB, tearDownDB, setUp_MortgageDocuments
from integration_tests.deed.deed_data import valid_deed
import copy
import requests
from application import config


class TestDeedRoutes(unittest.TestCase):
    webseal_headers = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Devices,O=1359.2.1,C=gb"
    }

    webseal_headers_2 = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Test,O=1360,C=gb"
    }

    webseal_headers_internal = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Test,O=*,C=gb"
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

        self.assertIn("title_number", str(created_deed))
        self.assertIn("borrowers", str(created_deed))
        self.assertIn("forename", str(created_deed))
        self.assertIn("surname", str(created_deed))
        self.assertIn("charge_clause", str(created_deed))
        self.assertIn("additional_provisions", str(created_deed))
        self.assertIn("lender", str(created_deed))
        self.assertIn("property_address", str(created_deed))

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
