import unittest
import requests
import json

from application import config
from integration_tests.helper import setUpApp
from integration_tests.deed.deed_data import valid_deed, valid_deed_two_borrowers


class TestAppRoutes(unittest.TestCase):
    webseal_headers = {
        "Content-Type": "application/json",
        "Iv-User-L": "CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=testusers,O=1359.2.1,C=gb"
    }

    def setUp(self):
        setUpApp(self)

    def test_health_service_check(self):
        test_health_check = requests.get(config.DEED_API_BASE_HOST + "/health/service-check")
        test_health_list = json.loads(test_health_check.text)

        self.assertEqual(test_health_check.status_code, 200)

        # Assert that there is a minimum of 4 service responses
        # Which are: register/title adapter, esec-client and postgres
        self.assertEqual(True, True) if len(test_health_list["services"]) >= 4 else self.assertEqual(False, True)

        # Assert that there is only one "services" tag; which is essentially a tag
        # that has an array of services as a value
        self.assertEqual(len(test_health_list), 1)

        # Test that certain tags/values are present
        self.assertIn("service_from", str(test_health_list["services"]))
        self.assertIn("service_to", str(test_health_list["services"]))
        self.assertIn("status_code", str(test_health_list["services"]))
        self.assertIn("service_message", str(test_health_list["services"]))

        # Test that the return json is not empty
        self.assertIsNotNone(test_health_list)

        # Test that the returned json is converted to a dictionary correctly
        self.assertIsInstance(test_health_list, dict)

    def test_get_deed_by_status_draft(self):
        get_existing_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/DRAFT',
                                          headers=self.webseal_headers)

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        get_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/DRAFT',
                                 headers=self.webseal_headers)
        self.assertEqual(get_deeds.status_code, 200)

        self.assertGreater(int(get_deeds.text), int(get_existing_deeds))

    def test_get_all_deeds(self):
        get_existing_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/%',
                                          headers=self.webseal_headers)

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=self.webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        get_all_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/%',
                                     headers=self.webseal_headers)
        self.assertEqual(get_all_deeds.status_code, 200)

        self.assertGreater(int(get_all_deeds.text), int(get_existing_deeds))

    def test_get_signed_deeds(self):
        get_existing_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/ALL-SIGNED',
                                          headers=self.webseal_headers)

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

        test_result = requests.get(config.DEED_API_BASE_HOST + '/dashboard/ALL-SIGNED',
                                   headers=self.webseal_headers)

        self.assertGreater(int(test_result.text), int(get_existing_deeds))

    def test_get_partially_signed_deeds(self):
        get_existing_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/PARTIALLY_SIGNED',
                                          headers=self.webseal_headers)

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed_two_borrowers),
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

        test_result = requests.get(config.DEED_API_BASE_HOST + '/dashboard/PARTIALLY_SIGNED',
                                   headers=self.webseal_headers)

        self.assertGreater(int(test_result.text), int(get_existing_deeds))
