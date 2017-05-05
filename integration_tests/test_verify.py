import unittest
import requests
import json
from application import config

from integration_tests.helper import setUpApp, insert_verify_match_row, webseal_headers


# This class tests the methods that remove the verify match row.
class TestVerifyMatchRemoval(unittest.TestCase):

    def setUp(self):
        setUpApp(self)
        insert_verify_match_row(self)

    def test_verify_removes_match(self):
        # Remove the match using the /verify-match/delete/<verify_pid> route
        response = requests.delete(config.DEED_API_BASE_HOST + '/borrower/verify-match/delete/200abc123',
                                   headers=webseal_headers).text
        self.assertEquals(json.loads(response)['result'], 'match found for PID 200abc123: row removed')

        # Call the route again to ensure that the row is no longer there
        response = requests.delete(config.DEED_API_BASE_HOST + '/borrower/verify-match/delete/200abc123',
                                   headers=webseal_headers).text
        self.assertEquals(json.loads(response)['result'], 'no match found for PID 200abc123: nothing removed')
