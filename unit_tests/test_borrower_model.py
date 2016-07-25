import unittest
from application.borrower.model import Borrower


class TestBorrowerModel(unittest.TestCase):

    def test_borrower_token(self):
        token = Borrower.generate_token()
        char_list = ['I', 'O', 'W', 'Z']
        res = False

        if any((c in char_list) for c in token):
            res = True

        self.assertTrue(token.isupper())
        self.assertFalse(res)
