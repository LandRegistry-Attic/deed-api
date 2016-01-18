#!/usr/local/bin/python

from os import listdir
from os.path import isfile, join
import csv
import os
import argparse
from sqlalchemy import create_engine, MetaData, Table, exc, bindparam

settings = []


def build_data(cols, row):
    data = {}
    idx = 0
    for col in cols:
        data[col] = row[idx]
        idx = idx +1
    return [data]


def process_input_options():
    parser = argparse.ArgumentParser(prog='data_importer', description='import data into db.')
    parser.add_argument('import_directory', default='.', metavar='/path/path',
                       help='import path relative to the executable')
    parser.add_argument('database_name',  metavar='database name',
                       help='name of the database instance to use e.g. deed_api')
    parser.add_argument('table_name', metavar='table name',
                       help='name of the table to which the data will be imported')
    parser.add_argument('--file_extension', '-ext', default='csv', metavar='csv',
                       help='extension type of the text files to import e.g. csv')
    parser.add_argument('-h','--help', 'utility to import all files of a given type (csv) '
                                       'in a given directory to a particular postgres sql table. '
                                       'The first row in the file indicates the column names to import ')

    settings = parser.parse_args()
    print(vars(settings))


def run_import():

    process_input_options()

    target_path = os.path.dirname(os.path.realpath(__file__)) + settings.import_directory

    target_file_list = [f for f in listdir(target_path) if isfile(join(target_path, f))]

    engine = create_engine(settings.database_name, convert_unicode=True)
    metadata = MetaData(bind=engine)
    table = Table(settings.table_name, metadata, autoload=True)
    con = engine.connect()

    cols=[]
    error_count = 0
    insert_count = 0
    update_count = 0
    total_rows=0

    with open(target_path + "/" + target_file_list[0], newline='') as csvfile:

        rows_reader = csv.reader(csvfile, delimiter='|', quotechar="'")
        row_count = 0

        for row in rows_reader:
            if row_count == 0:
                # The first row contains column names
                # which we cache
                cols = row
            else:
                total_rows += 1
                data = build_data(cols, row)
                try:
                    # Insert the row
                    con.execute(table.insert(), data)
                    insert_count += 1
                except exc.IntegrityError:
                    # update an existing row
                    stmt = table.update().\
                        where(table.c[cols[0]] == bindparam('old_'+cols[0])).\
                        values({'data': bindparam('data'),})

                    data[0]["old_"+cols[0]] = data[0][cols[0]]
                    con.execute(stmt, data)
                    update_count += 1
                except:
                    error_count += 1
            row_count += 1

    print("Row Count: "+ str(total_rows))
    print("Insert Count: "+ str(insert_count))
    print("Update Count: "+ str(update_count))
    print("Error Count: "+ str(error_count))


if __name__ == "__main__":
    run_import()