#! /usr/bin/env bash
echo "setting env_dir"
env_dir="$JENKINS_HOME/virtualenv/${JOB_NAME// /_}"

echo "create and activate a virtualenv"
#create and activate a virtualenv
virtualenv $env_dir
. $env_dir/bin/activate

echo "install requirements"
#install requirements
pip install -r requirements.txt

echo "install test only requirements"
#install test only requirements
pip install -r requirements_test.txt

echo "run tests.sh"
./test.sh

test_pass=$?

echo "run liniting"
./run_linting.sh

python_linting=$?

echo "set coverage"
coverage xml
coverage -rm

e_code=$((test_pass + python_linting))

exit $e_code
