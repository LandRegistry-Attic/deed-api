from functools import wraps
from application import app
from application import db
from flask.ext.script import Manager


def with_client(test):
    @wraps(test)
    def _wrapped_test(self):
        with self.app.test_client() as client:
            test(self, client)
    return _wrapped_test


def setUpApp(self):
    manager = Manager(app)
    self.app = manager.app
    self.manager = manager
    self.app.config['TESTING'] = True


def setUpDB(self):
    with self.app.app_context():
        db.create_all()


def tearDownDB(self):
    with self.app.app_context():
        db.session.remove()
        db.drop_all()
