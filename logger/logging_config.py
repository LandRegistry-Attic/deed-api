import json
from logging.config import dictConfig  # type: ignore
from logger.utils import call_once_only


@call_once_only
def setup_logging():
    try:
        with open('logger/logging_config.json', 'rt') as file:
            config = json.load(file)
            dictConfig(config)
    except IOError as e:
        raise(Exception('Failed to load logging configuration', e))
