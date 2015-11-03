export SETTINGS="config.DevelopmentConfig"

py.test --junitxml=TEST-flask-app-medium.xml --cov-report term-missing --cov application tests
