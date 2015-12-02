export SETTINGS="config.DevelopmentConfig"

mkdir -p test-reports

py.test --junitxml=test-reports/TEST-UNIT-flask-app-medium.xml --cov-report term-missing --cov-report=html --cov application unit_tests
