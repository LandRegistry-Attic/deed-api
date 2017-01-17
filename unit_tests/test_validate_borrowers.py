# flake8: noqa

import unittest

import mock

from application.deed.validate_borrowers import compare_borrower_names, _unpack_borrowers, _unmatched_names, \
      _set_no_duplicates, BorrowerNamesDifferException

PAYLOAD = {
   "title_number": "GR515835",
   "md_ref": "e-MD12344",
   "borrowers": [
     {
          "forename": "Simon",
          "surname": "Tsang",
          "gender": "Male",
          "address": "2 The Street, Plymouth, PL1 2PP",
          "dob": "01/10/1976",
          "phone_number": "07900804888"
      }, {
           "forename": "Eddie",
           "middle_name": "David",
           "surname": "Davies",
           "gender": "Female",
           "address": "2 The Street, Plymouth, PL1 2PP",
           "dob": "01/12/1982",
           "phone_number": "07747742010"
       }
   ],
   "identity_checked": "Y",
   "property_address": "5 The Drive, This Town, This County, PL4 4TH"
}


class TestValidateBorrowers(unittest.TestCase):

    def test_unpack_borrowers(self):
        ret_val = _unpack_borrowers(PAYLOAD)
        self.assertEqual(ret_val, ["Simon Tsang", "Eddie David Davies"])

    @mock.patch('application.register_adapter.service.RegisterAdapter.get_proprietor_names')
    def test_validate_borrower_good(self, mock_register_adapter):
        mock_register_adapter.return_value = ["Simon Tsang", "Eddie David Davies"]
        compare_borrower_names(PAYLOAD)

    @mock.patch('application.register_adapter.service.RegisterAdapter.get_proprietor_names')
    def test_validate_borrower_bad(self, mock_register_adapter):
        mock_register_adapter.return_value = ["Alice", "Bob"]
        self.assertRaises(BorrowerNamesDifferException, compare_borrower_names, PAYLOAD)


class TestValidateNames(unittest.TestCase):
    def test_names_register_names_proprietor_names(self):
        ret_val = _unmatched_names(['PeTeR', 'PaUl', 'MaRy'],
                                   ['pAuL', 'mArY', 'pEtEr'])
        self.assertFalse(ret_val)

    def test_more_names_on_register(self):
        ret_val = _unmatched_names(['Peter', 'Paul', 'Mary'],
                                   ['Peter'])
        self.assertEqual({'paul.0', 'mary.0'}, ret_val)

    def test_more_names_on_deed(self):
        ret_val = _unmatched_names(['Peter', 'Paul', 'Mary'],
                                   ['Peter', 'Mary', 'Paul', 'Bob'])

        self.assertEqual({'bob.0'}, ret_val)

    def test_dupes_on_register_subset_of_deed(self):
        ret_val = _unmatched_names(['Peter', 'Peter', 'Peter'],
                                   ['Peter', 'Paul', 'Mary'])
        self.assertEqual({'peter.1', 'peter.2', 'paul.0', 'mary.0'}, ret_val)

    def test_uniquify(self):
        names = _set_no_duplicates(['foo', 'foo', 'bar', 'Foo', 'Bar'])
        self.assertEqual({'foo.0', 'foo.1', 'bar.0', 'foo.2', 'bar.1'}, names)

    def test_all_borrower_names_present(self):
        pass
