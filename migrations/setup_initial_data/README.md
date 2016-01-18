#data_importer

Utility to import all files of a given type (csv), in a given directory
to a particular postgres sql table. The first row in the file indicates
the column names to import.

example usage:

python3 data_importer.py /data/mortgage_document postgresql://localhost:5432/deed_api mortgage_document


where:

directory_name = /data/mortgage_document
database_instance = postgresql://localhost:5432/deed_api
table_name = mortgage_document


CSV files are in the following format:

md_ref|data
e-MD12344|{"custom_data":"goes here}


The first row contains the column names that match the table definition
The field separator is the '|' symbol

Each row after the column header is inserted if new or updated if the row exists.

