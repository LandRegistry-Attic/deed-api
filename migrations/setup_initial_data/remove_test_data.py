#!/usr/local/bin/python3
import argparse
import application
from sqlalchemy import create_engine

DB = "postgresql://vagrant:vagrant@localhost:5432/deed_api"


def process_input_options():
    parser = argparse.ArgumentParser(prog='title_number_teardown', description='utility to remove '
                                     'all acceptance test title numbers.')
    parser.add_argument('element', metavar='element',
                        help='prefix of the test title numbers to be removed')
    parser.add_argument('prefix', metavar='prefix',
                        help='prefix of the test title numbers to be removed')
    parser.add_argument('confirm', metavar='confirm',
                        help="confirms you want to execute the delete")

    settings = parser.parse_args()
    return settings


def run_teardown():
    application.app.logger.info("Data Teardown Init")
    settings = process_input_options()
    application.app.logger.info("Settings from command line: %s" % str(settings))

    if settings.confirm is not None:
        engine = create_engine(DB, convert_unicode=True)
        sql_connection = engine.connect()

        sql_text = ("DELETE FROM deed WHERE deed ->> %s LIKE %s;")

        try:
            params = (settings.element, settings.prefix + "%")
            res = sql_connection.execute(sql_text, params)
            print("Deleted %s rows" % res.rowcount)
            return 1
        except:
            print("unable to execute SQL")
            return 0


if __name__ == "__main__":
    run_teardown()
