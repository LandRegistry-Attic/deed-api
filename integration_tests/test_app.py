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
        test_health_json = json.loads(test_health_check.text)

        self.assertEqual(test_health_check.status_code, 200)

        expectedAmount = False

        # Assert that there is a minimum of 3 service responses
        # This supposes that there may be a case where esec and title adapter stub/api
        # will be unavailable and will return a 500
        if(len(test_health_json["services"]) >= 3):
            expectedAmount = True

        self.assertEqual(expectedAmount, True)
