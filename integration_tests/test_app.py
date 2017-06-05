import unittest
import requests
import json
import time

from application import config
from integration_tests.helper import setUpApp, webseal_headers
from integration_tests.deed.deed_data import valid_deed, valid_deed_two_borrowers


class TestAppRoutes(unittest.TestCase):

    def setUp(self):
        setUpApp(self)

    def test_health_service_check(self):
        test_health_check = requests.get(config.DEED_API_BASE_HOST + "/health/service-check")
        test_health_list = json.loads(test_health_check.text)

        self.assertEqual(test_health_check.status_code, 200)

        # Assert that there is a minimum of 5 service responses
        # Which are: register/title adapter, esec-client, organisation-api and postgres
        self.assertEqual(True, True) if len(test_health_list["services"]) >= 5 else self.assertEqual(False, True)

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
                                          headers=webseal_headers)

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        get_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/DRAFT',
                                 headers=webseal_headers)
        self.assertEqual(get_deeds.status_code, 200)

        self.assertGreater(int(get_deeds.text), int(get_existing_deeds.text))

    def test_get_all_deeds(self):
        get_existing_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/%',
                                          headers=webseal_headers)

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        get_all_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/%',
                                     headers=webseal_headers)
        self.assertEqual(get_all_deeds.status_code, 200)

        self.assertGreater(int(get_all_deeds.text), int(get_existing_deeds.text))

    def test_get_signed_deeds(self):
        get_existing_deeds = requests.get(config.DEED_API_BASE_HOST + '/deed/retrieve-signed',
                                          headers=webseal_headers)

        get_existing_deeds = get_existing_deeds.json()

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed),
                                    headers=webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()

        code_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"]
        }

        request_code = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/request-auth-code',
                                     data=json.dumps(code_payload),
                                     headers=webseal_headers)

        self.assertEqual(request_code.status_code, 200)

        sign_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"],
            "authentication_code": "aaaa"
        }

        sign_deed = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/verify-auth-code',
                                  data=json.dumps(sign_payload),
                                  headers=webseal_headers)

        self.assertEqual(sign_deed.status_code, 200)

        get_deed_again = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                      headers=webseal_headers)

        second_deed = get_deed_again.json()

        timer = time.time() + 15
        while time.time() < timer or second_deed["deed"]["status"] != "ALL-SIGNED":
            get_deed_again = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                          headers=webseal_headers)

            second_deed = get_deed_again.json()

        test_result = requests.get(config.DEED_API_BASE_HOST + '/deed/retrieve-signed',
                                   headers=webseal_headers)

        test_result = test_result.json()

        self.assertGreater(len(test_result["deeds"]), len(get_existing_deeds["deeds"]))

    def test_get_partially_signed_deeds(self):
        get_existing_deeds = requests.get(config.DEED_API_BASE_HOST + '/dashboard/PARTIALLY_SIGNED',
                                          headers=webseal_headers)

        create_deed = requests.post(config.DEED_API_BASE_HOST + '/deed/',
                                    data=json.dumps(valid_deed_two_borrowers),
                                    headers=webseal_headers)
        self.assertEqual(create_deed.status_code, 201)

        response_json = create_deed.json()

        get_created_deed = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                        headers=webseal_headers)

        self.assertEqual(get_created_deed.status_code, 200)

        created_deed = get_created_deed.json()

        code_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"]
        }

        request_code = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/request-auth-code',
                                     data=json.dumps(code_payload),
                                     headers=webseal_headers)

        self.assertEqual(request_code.status_code, 200)

        sign_payload = {
            "borrower_token": created_deed["deed"]["borrowers"][0]["token"],
            "authentication_code": "aaaa"
        }

        sign_deed = requests.post(config.DEED_API_BASE_HOST + response_json["path"] + '/verify-auth-code',
                                  data=json.dumps(sign_payload),
                                  headers=webseal_headers)

        self.assertEqual(sign_deed.status_code, 200)

        get_deed_again = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                      headers=webseal_headers)

        second_deed = get_deed_again.json()

        timer = time.time() + 15
        while time.time() < timer or second_deed["deed"]["status"] != "PARTIALLY-SIGNED":
            get_deed_again = requests.get(config.DEED_API_BASE_HOST + response_json["path"],
                                          headers=webseal_headers)

            second_deed = get_deed_again.json()

        test_result = requests.get(config.DEED_API_BASE_HOST + '/dashboard/PARTIALLY_SIGNED',
                                   headers=webseal_headers)

        self.assertGreater(int(test_result.text), int(get_existing_deeds.text))
