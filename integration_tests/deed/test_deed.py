import json
import unittest
from integration_tests.helper import with_client, setUpApp, setUpDB, tearDownDB, setUp_MortgageDocuments
from application.borrower.server import BorrowerService


class TestDeedRoutes(unittest.TestCase):

    def setUp(self):
        setUpApp(self)
        setUpDB(self)

    def tearDown(self):
        tearDownDB(self)

    @with_client
    def test_deed_create_and_get(self, client):

        setUp_MortgageDocuments(self)

        valid_deed = {
            "title_number": "DN100",
            "md_ref": "e-MD123G",
            "address": "5 The Drive, This Town, This County, PL4 4TH",
            "borrowers": [
                {
                    "forename": "lisa",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "Male",
                    "address": "test address with postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154062"
                },
                {
                    "forename": "frank",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "Female",
                    "address": "Test Address With Postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154061"
                }
            ],
            "identity_checked": "Y"
        }

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
        self.assertIn("charge_clause", str(get_created_deed.data))
        self.assertIn("additional_provisions", str(get_created_deed.data))
        self.assertIn("lender", str(get_created_deed.data))
        self.assertIn("address", str(get_created_deed.data))

    @with_client
    def test_bad_get(self, client):
        fake_token_deed = client.get("/deed/fake")

        self.assertEqual(fake_token_deed.status_code, 404)
        self.assertIn("Not Found", str(fake_token_deed.data))

    @with_client
    def test_deed_without_borrowers(self, client):

        deed_without_borrowers = {
            "title_number": "DN100",
            "md_ref": "e-MD123G",
            "address": "5 The Drive, This Town, This County, PL4 4TH",
            "borrowers": [
            ]
        }

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_borrowers),
                                  headers={'content-type': 'application/json'})
        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_without_title(self, client):

        deed_without_title_number = {
            "md_ref": "e-MD123G",
            "identity_checked": "Y",
            "address": "5 The Drive, This Town, This County, PL4 4TH",
            "borrowers": [
                {
                    "forename": "lisa",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "Male",
                    "address": "test address with postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154062"
                },
                {
                    "forename": "frank",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "Female",
                    "address": "Test Address With Postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154061"
                }
            ]
        }

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_title_number),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_with_missing_borrower_properties(self, client):

        deed_with_invalid_borrower = {
            "title_number": "DN100",
            "md_ref": "e-MD123G",
            "identity_checked": "Y",
            "address": "5 The Drive, This Town, This County, PL4 4TH",
            "borrowers": [
                {
                    "forename": "lisa"
                }
            ]
        }

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_with_invalid_borrower),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_without_md_ref(self, client):

        deed_without_md_ref = {
            "title_number": "DN100",
            "identity_checked": "Y",
            "address": "5 The Drive, This Town, This County, PL4 4TH",
            "borrowers": [
                {
                    "forename": "lisa",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "Male",
                    "address": "test address with postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154062"
                },
                {
                    "forename": "frank",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "Female",
                    "address": "Test Address With Postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154061"
                }
            ]
        }

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_md_ref),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_without_address(self, client):

        deed_without_address = {
            "title_number": "DN100",
            "md_ref": "e-MD123G",
            "borrowers": [
                {
                    "forename": "lisa",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "Male",
                    "address": "test address with postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154062"
                },
                {
                    "forename": "frank",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "Female",
                    "address": "Test Address With Postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154061"
                }
            ]
        }

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_address),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_with_unknown_md_ref(self, client):

        deed_with_unknown_md_ref = json.loads(
            '{'
            '   "title_number": "DN100",'
            '   "md_ref": "e-MD111G",'
            '   "identity_checked": "Y",'
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
                                  data=json.dumps(deed_with_unknown_md_ref),
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
        newBorrower = borrowerService.saveBorrower(borrower, "aaaaaa")
        response = client.delete('/deed/borrowers/delete/'+str(newBorrower.id))

        self.assertEqual(response.status_code, 200)

    @with_client
    def test_delete_borrower_none_exists(self, client):

        response = client.delete('/deed/borrowers/delete/999999999')

        self.assertEqual(response.status_code, 404)

    @with_client
    def test_validate_borrower(self, client):
        borrowerService = BorrowerService()

        borrower = {
            "forename": "lisa",
            "deed_token": "aaaaaa",
            "token": "bbbbbb",
            "middle_name": "ann",
            "surname": "bloggette",
            "gender": "Male",
            "address": "test address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154062"
        }

        newBorrower = borrowerService.saveBorrower(borrower, "aaaaaa")
        response = client.post('/borrower/validate',
                               data=json.dumps({"borrower_token":
                                                newBorrower.token,
                                                "dob": "23/01/1986"}),
                               headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 200)

    @with_client
    def test_validate_borrower_not_found(self, client):

        response = client.post('/borrower/validate',
                               data=json.dumps({"borrower_token": "unknown",
                                                "dob": "23/01/1986"}),
                               headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), "Matching deed not found")
