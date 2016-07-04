import json
import os
from logging.config import dictConfig  # type: ignore
from logger.utils import call_once_only


@call_once_only
def setup_logging():
    try:
        dirname = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dirname, 'logging_config.json'), 'rt') as file:
            config = json.load(file)
            log_path = os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])[0]
            config['handlers']['log_file']['filename'] = \
                os.path.join(log_path, 'logs/dm-api-info.log')
            dictConfig(config)
    except IOError as e:
        raise(Exception('Failed to load logging configuration', e))
