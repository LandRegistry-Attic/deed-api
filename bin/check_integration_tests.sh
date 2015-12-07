#! /usr/bin/bash

virtualenv integration_test_env

source ./integration_test_env/bin/activate

pip3 install -r requirements.txt

integration_tests_pass="./integration_test.sh"

if $integration_tests_pass; then
  deactivate
  echo "Integration tests PASSED!!! Exiting"
  exit 0
else
  deactivate
  echo "Integration tests FAILED!!! Exiting"
  exit 1
fi
