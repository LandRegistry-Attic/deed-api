#! /usr/bin/env bash

export SETTINGS="config.DevelopmentConfig"

env_dir="$JENKINS_HOME/virtualenv/${JOB_NAME// /_}"

#create and activate a virtualenv
virtualenv $env_dir
. $env_dir/bin/activate

#install requirements
pip install -r requirements.txt

py.test --junitxml=TEST-INT-flask-app-medium.xml --cov-report term-missing --cov application integration_tests

integration_test_pass=$?

e_code=$((integration_test_pass))

exit $e_code

