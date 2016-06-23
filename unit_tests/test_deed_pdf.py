import unittest

from application import app
from application.deed.deed_format import create_deed_html
from unit_tests.helper import DeedModelMock


class TestDeedPdf(unittest.TestCase):

    def test_create_deed_html(self):
        deed = DeedModelMock
        with app.app_context():
            self.assertTrue('Digital Mortgage Deed' in create_deed_html(deed.deed))