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
            application_path = os.path.split(os.path.abspath('application'))[0]
            project_path = os.path.split(application_path)[0]
            config['handlers']['log_file']['filename'] = \
                os.path.join(project_path, 'logs/dm-api-info.log')

            dictConfig(config)
    except IOError as e:
        raise(Exception('Failed to load logging configuration', e))
