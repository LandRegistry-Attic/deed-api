export SETTINGS="config.DevelopmentConfig"

py.test --junitxml=TEST-INT-flask-app-medium.xml --cov-report term-missing --cov application integration_tests
