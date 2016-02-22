import os

DEBUG = os.getenv("DEBUG", True)
SQLALCHEMY_DATABASE_URI = os.getenv('DEED_DATABASE_URI',
                                    'postgres:///deed_api')

AKUMA_BASE_HOST = os.getenv('AKUMA_ADDRESS',
                      'http://10.10.10.10:5055')
