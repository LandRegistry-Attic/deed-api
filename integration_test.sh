export SETTINGS="config.DevelopmentConfig"

py.test --junitxml=TEST-INT-flask-app-medium.xml --cov-report term-missing --cov application integration_tests

python3 manage.py db upgrade

DATABASE_URL="${DEED_DATABASE_URI:-postgresql://vagrant:vagrant@localhost:5432/deed_api}"

# Mortgage document - upserts of md_ref's data
python3 ./migrations/setup_initial_data/data_importer.py /data/mortgage_document/ $DATABASE_URL mortgage_document