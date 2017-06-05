import unittest
import requests
import json
from application import config

from integration_tests.helper import setUpApp, insert_verify_match_row, webseal_headers, insert_borrower_row, remove_borrower_row


# This class tests the methods that remove the verify match row.
class TestVerifyMatchRemoval(unittest.TestCase):

    def setUp(self):
        setUpApp(self)
        insert_borrower_row(self, 'verify_pid', 999)
        insert_verify_match_row(self, 'verify_pid', 999)

    def test_verify_removes_match(self):
        # Remove the match using the /verify-match/delete/<verify_pid> route
        response = requests.delete(config.DEED_API_BASE_HOST + '/borrower/verify-match/delete/verify_pid',
                                   headers=webseal_headers).text
        self.assertEquals(json.loads(response)['result'], 'match found for PID provided.')

        # Call the route again to ensure that the row is no longer there
        response = requests.delete(config.DEED_API_BASE_HOST + '/borrower/verify-match/delete/verify_pid',
                                   headers=webseal_headers).text
        self.assertEquals(json.loads(response)['result'], 'no match found for PID provided.')

    def tearDown(self):
        remove_borrower_row(self, 999)
