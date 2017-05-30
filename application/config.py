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

DEED_API_BASE_HOST = os.getenv('DEED_API_ADDRESS', 'http://0.0.0.0:9020')

ORGANISATION_API_BASE_HOST = os.getenv('ORGANISATION_API_ADDRESS', 'http://localhost:9060')

# For logging
FLASK_LOG_LEVEL = os.environ['LOG_LEVEL']

LOGCONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            '()': 'application.extensions.JsonFormatter'
        },
        'audit': {
            '()': 'application.extensions.JsonAuditFormatter'
        }
    },
    'filters': {
        'contextual': {
            '()': 'application.extensions.ContextualFilter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['contextual'],
            'stream': 'ext://sys.stdout'
        },
        'audit_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'audit',
            'filters': ['contextual'],
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'application': {
            'handlers': ['console'],
            'level': FLASK_LOG_LEVEL
        },
        'audit': {
            'handlers': ['audit_console'],
            'level': 'INFO'
        }
    }
}