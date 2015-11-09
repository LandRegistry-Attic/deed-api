import os

DEBUG = os.getenv("DEBUG", True)
SQLALCHEMY_DATABASE_URI = os.getenv('DEED_DATABASE_URI',
                                    'postgres:///deed_api')
