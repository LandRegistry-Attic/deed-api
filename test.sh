export SETTINGS="config.DevelopmentConfig"

mkdir -p test-reports

py.test --junitxml=test-reports/TEST-dm-deed-api.xml --cov-report term-missing --cov application tests
