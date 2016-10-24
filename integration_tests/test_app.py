import unittest
import requests
import json

from application import config
from integration_tests.helper import setUpApp


class TestAppRoutes(unittest.TestCase):

    def setUp(self):
        setUpApp(self)

    def test_health_service_check(self):
        test_health_check = requests.get(config.DEED_API_BASE_HOST + '/health/service-check')
        test_health_list = json.loads(test_health_check.text)

        self.assertEqual(test_health_check.status_code, 200)

        expectedAmount = False

        # Assert that there is a minimum of 4 service responses
        # Which are: register/title adapter, esec-client and postgres
        if(len(test_health_list["services"]) >= 4):
            expectedAmount = True

        self.assertEqual(expectedAmount, True)

        # Assert that there is only one "services" tag; which is essentially a tag
        # that has an array of services as a value
        self.assertEqual(len(test_health_list), 1)

        # Test that certain tags/values are present
        self.assertIn("deed-api", str(test_health_list['services']))
        self.assertIn("title-adapter", str(test_health_list['services']))
        self.assertIn("register-adapter", str(test_health_list['services']))
        self.assertIn("esec-client", str(test_health_list['services']))

        self.assertIn("service_from", str(test_health_list['services']))
        self.assertIn("service_to", str(test_health_list['services']))
        self.assertIn("status_code", str(test_health_list['services']))
        self.assertIn("service_message", str(test_health_list['services']))

        # Test that the return json is not empty
        self.assertIsNotNone(test_health_list)

        # Test that the returned json is converted to a dictionary correctly
        self.assertIsInstance(test_health_list, dict)
