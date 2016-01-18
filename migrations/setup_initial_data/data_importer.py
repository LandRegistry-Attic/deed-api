#!/usr/local/bin/python3
import csv
import os
import argparse
from os import listdir
from os.path import isfile, join
from sqlalchemy import create_engine, MetaData, Table, exc, bindparam
import logging

LOGGER = logging.getLogger(__name__)


def build_data(cols, row):
    data = {}
    for idx, col in enumerate(cols):
        data[col] = row[idx]
    return [data]


def process_input_options():
    parser = argparse.ArgumentParser(
            prog='data_importer', description='utility to import all '
            'files of a given type (csv) in a given'
            'directory to a particular postgres sql table. The first row '
            'in the file indicates the column names to import.')
    parser.add_argument('import_directory', default='.', metavar='/path/path',
                        help='import path relative to the executable')
    parser.add_argument('database_name', metavar='database_name',
                        help='name of the database instance to use e.g. deed_api')
    parser.add_argument('table_name', metavar='table_name',
                        help='name of the table to which the data will be imported')
    parser.add_argument('--file_extension', '-ext', default='csv', metavar='csv',
                        help='extension type of the text files to import e.g. csv')

    settings = parser.parse_args()
    return settings


def upsert(sql_connection, table, data, column_names):
    try:
        sql_connection.execute(table.insert(), data)
        return 1
    except exc.IntegrityError:
        stmt = table.update(). \
            where(table.c[column_names[0]] == bindparam('old_' + column_names[0])).\
            values({'data': bindparam('data')})

        data[0]["old_" + column_names[0]] = data[0][column_names[0]]
        sql_connection.execute(stmt, data)
        return 2
    except:
        return 0


def process_file(csv_file, sql_connection, table):
    column_names = []
    error_count = 0
    insert_count = 0
    update_count = 0
    total_rows = 0

    print("\nProcessing: %s" % csv_file.name)
    LOGGER.info("Processing file: %s" % str(csv_file.name))

    rows_reader = csv.reader(csv_file, delimiter='|', quotechar="'")
    row_count = 0

    for row in rows_reader:
        if row_count == 0:
            # The first row contains column names
            column_names = row
        else:
            total_rows += 1
            data = build_data(column_names, row)
            res = upsert(sql_connection, table, data, column_names)

            if res == 1:
                insert_count += 1
            elif res == 2:
                update_count += 1
            else:
                error_count += 1

        row_count += 1

    print("Row Count: " + str(total_rows))
    print("Insert Count: " + str(insert_count))
    print("Update Count: " + str(update_count))
    print("Error Count: " + str(error_count))
    LOGGER.info("Processing file complete, errors: %s" % str(error_count))

    print("-" * 120)


def run_import():
    LOGGER.info("Data Importer Init")
    settings = process_input_options()
    LOGGER.info("Settings from command line: %s" % str(settings))

    target_path = os.path.dirname(os.path.realpath(__file__)) + settings.import_directory

    target_file_list = [f for f in listdir(target_path) if isfile(join(target_path, f))]

    engine = create_engine(settings.database_name, convert_unicode=True)
    metadata = MetaData(bind=engine)
    table = Table(settings.table_name, metadata, autoload=True)
    sql_connection = engine.connect()

    with open(target_path + "/" + target_file_list[0], newline='') as csv_file:
        process_file(csv_file, sql_connection, table)


if __name__ == "__main__":
    run_import()
