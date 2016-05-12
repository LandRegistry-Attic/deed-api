import unittest
import json
import os
import re


class TestPropertyAddress(unittest.TestCase):

    def setUp(self):
        dirname = os.path.dirname(os.path.abspath(__file__))
        fqname = os.path.join(os.path.split(dirname)[0],
                              'application',
                              'deed',
                              'schemas',
                              'deed-api.json')
        schema = json.loads(open(fqname).read())
        _dict = schema["definitions"]["Deed_Application"]
        self.pattern = _dict["properties"]['property_address']['pattern']

    def test_special_chars(self):
        address = re.match(self.pattern,
                           'Chalon-Sur-Saône, Westward Ho!, Devon')
        self.assertTrue(address)

    def test_empty_string(self):
        address = re.match(self.pattern, '')
        self.assertFalse(address)

if __name__ == "__main__":
    unittest.main()
