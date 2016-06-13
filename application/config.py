import os

DEBUG = os.getenv("DEBUG", True)
SQLALCHEMY_DATABASE_URI = os.getenv('DEED_DATABASE_URI',
                                    'postgres:///deed_api')

AKUMA_BASE_HOST = os.getenv('AKUMA_ADDRESS',
                            'http://127.0.0.1:5055')

ESEC_CLIENT_BASE_HOST = os.getenv('ESEC_CLIENT_URI', 'http://127.0.0.1:9040')

ESEC_SCHEMA_LOCATION = os.getenv('ESEC_SCHEMA_LOCATION', 'http://localhost:9080/schemas/')

TITLE_ADAPTOR_BASE_HOST = os.getenv('TITLE_ADAPTOR_URI', 'http://localhost:5010')

DM_REGISTER_ADAPTER = os.getenv('REGISTER_ADAPTER', 'http://localhost:5011/')
