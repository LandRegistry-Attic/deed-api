import json
import unittest
from integration_tests.helper import with_client, setUpApp, setUpDB, tearDownDB
from application.borrower.server import BorrowerService


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
            '   "md_ref": "e-MD123G",'
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

        response_json = json.loads(create_deed.data.decode())
        get_created_deed = client.get(response_json["url"])
        self.assertEqual(get_created_deed.status_code, 200)

        self.assertIn("title_number", str(get_created_deed.data))
        self.assertIn("borrowers", str(get_created_deed.data))
        self.assertIn("forename", str(get_created_deed.data))
        self.assertIn("surname", str(get_created_deed.data))

    @with_client
    def test_bad_get(self, client):
        fake_token_deed = client.get("/deed/fake")

        self.assertEqual(fake_token_deed.status_code, 404)
        self.assertIn("Not Found", str(fake_token_deed.data))

    @with_client
    def test_deed_without_borrowers(self, client):

        deed_without_borrowers = json.loads(
            '{'
            '   "title_number": "DN100",'
            '   "md_ref": "e-MD123G",'
            '   "borrowers": ['
            '   ]'
            '}'
        )

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_borrowers),
                                  headers={'content-type': 'application/json'})
        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_without_title(self, client):

        deed_without_title_number = json.loads(
            '{'
            '   "md_ref": "e-MD123G",'
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
                                  data=json.dumps(deed_without_title_number),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_with_missing_borrower_properties(self, client):

        deed_with_invalid_borrower = json.loads(
            '{'
            '   "title_number": "DN100",'
            '   "md_ref": "e-MD123G",'
            '   "borrowers": ['
            '       {'
            '           "forename": "lisa"'
            '       }'
            '   ]'
            '}'
        )

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_with_invalid_borrower),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_without_md_ref(self, client):

        deed_without_md_ref = json.loads(
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
                                  data=json.dumps(deed_without_md_ref),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_delete_borrower(self, client):

        borrowerService = BorrowerService()
        borrower = {
            "forename": "lisa",
            "middle_name": "ann",
            "surname": "bloggette",
            "gender": "Male",
            "address": "test address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154062"
        }
        newBorrower = borrowerService.saveBorrower(borrower)
        response = client.delete('/deed/borrowers/delete/'+str(newBorrower.id))

        self.assertEqual(response.status_code, 200)

    @with_client
    def test_delete_borrower_none_exists(self, client):

        response = client.delete('/deed/borrowers/delete/999999999')

        self.assertEqual(response.status_code, 404)
