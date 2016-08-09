# Get full path to the directory that this scripts is in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# By changing to the directory that this script is in means you no longer need to be in
# the directory to run these tests
cd $DIR

pip install -r requirements.txt

py.test --junitxml=TEST-INT-flask-app-medium.xml --verbose --cov-report term-missing --cov application integration_tests

RESULT=$?
# This file will prepare all dependancies for the application
DB_NAME="${DEED_DATABASE_NAME:-dm-deeds}"

# TODO Teardown not using psql but using sql instead

psql $DB_NAME -c "drop table alembic_version cascade;"
psql $DB_NAME -c "drop table deed cascade;"
psql $DB_NAME -c "drop table borrower cascade;"
psql $DB_NAME -c "drop table mortgage_document cascade;"

python3 manage.py db upgrade

DATABASE_URL="${DEED_DATABASE_URI:-postgresql://vagrant:vagrant@localhost:5432/deed_api}"

# Mortgage document - upserts of md_ref's data
python3 ./migrations/setup_initial_data/data_importer.py /data/mortgage_document/ $DATABASE_URL mortgage_document

exit $RESULT
