import json
import unittest
from integration_tests.helper import with_client, setUpApp, setUpDB, tearDownDB, setUp_MortgageDocuments
from application.borrower.server import BorrowerService
from integration_tests.deed.deed_data import valid_deed
import copy


class TestDeedRoutes(unittest.TestCase):

    def setUp(self):
        setUpApp(self)
        setUpDB(self)
        setUp_MortgageDocuments(self)

    def tearDown(self):
        tearDownDB(self)

    @with_client
    def test_deed_create_and_get(self, client):

        create_deed = client.post('/deed/',
                                  data=json.dumps(valid_deed),
                                  headers={'content-type': 'application/json'})
        self.assertEqual(create_deed.status_code, 201)
        self.assertIn("/deed/", str(create_deed.data))

        response_json = json.loads(create_deed.data.decode())
        get_created_deed = client.get(response_json["path"])
        self.assertEqual(get_created_deed.status_code, 200)

        self.assertIn("title_number", str(get_created_deed.data))
        self.assertIn("borrowers", str(get_created_deed.data))
        self.assertIn("forename", str(get_created_deed.data))
        self.assertIn("surname", str(get_created_deed.data))
        self.assertIn("charge_clause", str(get_created_deed.data))
        self.assertIn("additional_provisions", str(get_created_deed.data))
        self.assertIn("lender", str(get_created_deed.data))
        self.assertIn("property_address", str(get_created_deed.data))

    @with_client
    def test_bad_get(self, client):
        fake_token_deed = client.get("/deed/fake")

        self.assertEqual(fake_token_deed.status_code, 404)
        self.assertIn("Not Found", str(fake_token_deed.data))

    @with_client
    def test_deed_create_and_get_by_mdref_and_titleno(self, client):

        create_deed = client.post('/deed/',
                                  data=json.dumps(valid_deed),
                                  headers={'content-type': 'application/json'})
        self.assertEqual(create_deed.status_code, 201)
        self.assertIn("/deed/", str(create_deed.data))

        response_json = json.loads(create_deed.data.decode())
        get_created_deed = client.get("deed?md_ref=" + valid_deed["md_ref"] +
                                      "&title_number=" + valid_deed["title_number"])
        self.assertEqual(get_created_deed.status_code, 200)

        self.assertIn("token", str(get_created_deed.data))
        self.assertIn("status", str(get_created_deed.data))
        self.assertIn("DRAFT", str(get_created_deed.data))
        self.assertIn(response_json["path"][-6:], str(get_created_deed.data))

    @with_client
    def test_invalid_params_on_get_with_mdref_and_titleno(self, client):
        fake_token_deed = client.get("/deed?invalid_query_parameter=invalid")

        self.assertEqual(fake_token_deed.status_code, 400)
        self.assertIn("400 Bad Request", str(fake_token_deed.data))

    @with_client
    def test_invalid_query_params_on_get_with_mdref_and_titleno(self, client):
        fake_token_deed = client.get("/deed?md_ref=InvalidMD&title_number=InvalidTitleNo")

        self.assertEqual(fake_token_deed.status_code, 404)
        self.assertIn("Not Found", str(fake_token_deed.data))

    @with_client
    def test_deed_without_borrowers(self, client):

        deed_without_borrowers = copy.deepcopy(valid_deed)
        deed_without_borrowers["borrowers"] = []

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_borrowers),
                                  headers={'content-type': 'application/json'})
        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_without_title(self, client):

        deed_without_title_number = copy.deepcopy(valid_deed)
        del deed_without_title_number["title_number"]

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_title_number),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_with_missing_borrower_properties(self, client):

        deed_with_invalid_borrower = copy.deepcopy(valid_deed)
        deed_with_invalid_borrower["borrowers"] = [
            {
                "forename": "lisa"
            }
        ]

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_with_invalid_borrower),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_without_md_ref(self, client):

        deed_without_md_ref = copy.deepcopy(valid_deed)
        del deed_without_md_ref["md_ref"]

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_md_ref),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_without_address(self, client):

        deed_without_address = copy.deepcopy(valid_deed)
        del deed_without_address["property_address"]

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_without_address),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_deed_with_unknown_md_ref(self, client):

        deed_with_unknown_md_ref = copy.deepcopy(valid_deed)
        deed_with_unknown_md_ref["md_ref"] = "e-MD111G"

        create_deed = client.post('/deed/',
                                  data=json.dumps(deed_with_unknown_md_ref),
                                  headers={'content-type': 'application/json'})

        self.assertEqual(create_deed.status_code, 400)

    @with_client
    def test_delete_borrower(self, client):

        borrowerService = BorrowerService()
        borrower = valid_deed["borrowers"][0]

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

        borrower = valid_deed["borrowers"][0]

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
