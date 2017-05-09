import os
from flask.ext.script import Manager
from functools import wraps
from migrations.setup_initial_data.data_importer import process_file
from sqlalchemy import create_engine, MetaData, Table

from application import app
from application import db
from application.borrower.model import Borrower

webseal_headers = {
    "Content-Type": "application/json",
    os.getenv("WEBSEAL_HEADER_KEY"): os.getenv("WEBSEAL_HEADER_INT_TEST_4")
}


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
        manager = Manager(db)
        self.db = manager.db


def insert_verify_match_row(self, verify_pid, borrower_id):
    with self.app.app_context():
        db.engine.execute('DELETE FROM verify_match WHERE verify_pid = %s', verify_pid)
        db.engine.execute('INSERT INTO verify_match (verify_pid, borrower_id, confidence_level)' +
                          'VALUES (%s, %s, %s)', verify_pid, borrower_id, 3)


def insert_borrower_row(self, verify_pid, borrower_id):
    with self.app.app_context():
        remove_borrower_row(self, 999)
        borrower = Borrower()
        borrower.id = 999
        borrower.forename = 'some'
        borrower.middlename = 'nice'
        borrower.surname = 'guy'
        borrower.dob = 'a date'
        borrower.gender = 'a gender'
        borrower.phonenumber = '07777777777'
        borrower.address = 'an address'
        borrower.token = 'a token'
        borrower.deed_token = 'a deed token'
        borrower.esec_user_name = 'an esec user name'
        borrower.save()


def remove_borrower_row(self, borrower_id):
    with self.app.app_context():
        borrower = Borrower()
        borrower.delete(999)


def setUp_MortgageDocuments(self):

    uri = os.getenv("DEED_DATABASE_URI", "postgresql://vagrant:vagrant@localhost:5432/deed_api")

    engine = create_engine(uri, convert_unicode=True)
    metadata = MetaData(bind=engine)
    table = Table('mortgage_document', metadata, autoload=True)
    sql_connection = engine.connect()

    csv_file = open('./integration_tests/deed/test_md.csv', newline='')

    process_file(csv_file, sql_connection, table)


def tearDownDB(self):
    with self.app.app_context():
        db.session.remove()
        db.drop_all()
