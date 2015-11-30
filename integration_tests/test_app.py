# from application import app
# import unittest
# import os
#
# class TestRoutes(unittest.TestCase):
#
#     def setUp(self):
#         app.config.from_object(os.environ.get('SETTINGS'))
#         self.app = app.test_client()
#
#     def test_health(self):
#         self.assertEqual((self.app.get('/health')).status, '200 OK')
#
#     def test_deed(self):
#         self.assertEqual((self.app.get('/deed')).status, '301 MOVED PERMANENTLY')
