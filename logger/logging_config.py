import json
from logging.config import dictConfig  # type: ignore
from logger.utils import call_once_only
import os


@call_once_only
def setup_logging():
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")

        with open('logger/logging_config.json', 'rt') as file:
            config = json.load(file)
            dictConfig(config)
    except IOError as e:
        raise(Exception('Failed to load logging configuration', e))
