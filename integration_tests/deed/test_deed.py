import json
import unittest
from integration_tests.helper import with_client, setUpApp, setUpDB, tearDownDB
import logging


class TestDeedRoutes(unittest.TestCase):

    def setUp(self):
        setUpApp(self)
        setUpDB(self)

    def tearDown(self):
        tearDownDB(self)

    @with_client
    def test_deed_create_and_get(self, client):

        valid_deed = json.loads(
            '{'
            '   "title_number": "DN100",'
            '   "borrowers": ['
            '       {'
            '           "forename": "lisa",'
            '           "middle_name": "ann",'
            '           "surname": "bloggette",'
            '           "gender": "Male",'
            '           "address": "test address with postcode, PL14 3JR",'
            '           "dob": "23/01/1986",'
            '           "phone_number": "07502154062"'
            '       },'
            '       {'
            '           "forename": "frank",'
            '           "middle_name": "ann",'
            '           "surname": "bloggette",'
            '           "gender": "Female",'
            '           "address": "Test Address With Postcode, PL14 3JR",'
            '           "dob": "23/01/1986",'
            '           "phone_number": "07502154061"'
            '       }'
            '   ]'
            '}'
        )

        create_deed = client.post('/deed/',
                                  data=json.dumps(valid_deed),
                                  headers={'content-type': 'application/json'})
        self.assertEqual(create_deed.status_code, 201)
        self.assertIn("/deed/", str(create_deed.data))

        get_created_deed = client.get(create_deed.data)
        self.assertEqual(get_created_deed.status_code, 200)

        self.assertIn("title_number", str(get_created_deed.data))
        self.assertIn("borrowers", str(get_created_deed.data))
        self.assertIn("forename", str(get_created_deed.data))
        self.assertIn("surname", str(get_created_deed.data))
