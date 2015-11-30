import json
from logging.config import dictConfig  # type: ignore

done_setup = False


def setup_logging():
    global done_setup

    if not done_setup:
        try:
            logging_config_file_path = 'logger/logging_config.json'
            with open(logging_config_file_path, 'rt') as file:
                config = json.load(file)
            dictConfig(config)
            done_setup = True
        except IOError as e:
            raise(Exception('Failed to load logging configuration', e))
