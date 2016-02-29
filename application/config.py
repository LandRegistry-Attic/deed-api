import os

DEBUG = os.getenv("DEBUG", True)
SQLALCHEMY_DATABASE_URI = os.getenv('DEED_DATABASE_URI',
                                    'postgres:///deed_api')

AKUMA_BASE_HOST = os.getenv('AKUMA_ADDRESS',
                            'http://0.0.0.0:5055')

#Twilio Api interface details
#ACCOUNT_SID = "ACfcfc375748835920eb4ec115bfa3008f"
#AUTH_TOKEN = "52e3b53a462f3f184f50d90816c43e64"

ACCOUNT_SID = os.getenv('ACCOUNT_SID', '')
AUTH_TOKEN = os.getenv('AUTH_TOKEN', '')
account = ACCOUNT_SID
auth = AUTH_TOKEN
