import os

DEBUG = os.getenv("DEBUG", True)
SQLALCHEMY_DATABASE_URI = os.getenv('DEED_DATABASE_URI',
                                    'postgres:///deed_api')

AKUMA_BASE_HOST = os.getenv('AKUMA_ADDRESS',
                            'http://127.0.0.1:5055')

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
ESEC_CLIENT_BASE_HOST = os.getenv('ESEC_CLIENT_URI', 'http://127.0.0.1:5001')
