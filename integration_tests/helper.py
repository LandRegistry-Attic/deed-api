from functools import wraps
from application import app
from application import db
from flask.ext.script import Manager
from migrations.setup_initial_data.data_importer import process_file
from sqlalchemy import create_engine, MetaData, Table

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

def setUp_MortgageDocuments(self):
    engine = create_engine('postgresql://localhost:5432/deed_api', convert_unicode=True)
    metadata = MetaData(bind=engine)
    table = Table('mortgage_document', metadata, autoload=True)
    sql_connection = engine.connect()

    csv_file = open('./integration_tests/deed/test_md.csv', newline='')

    process_file(csv_file, sql_connection, table)

def tearDownDB(self):
    with self.app.app_context():
        db.session.remove()
        db.drop_all()
