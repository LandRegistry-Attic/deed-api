# Get full path to the directory that this scripts is in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# By changing to the directory that this script is in means you no longer need to be in
# the directory to run these tests 
cd $DIR

mkdir -p test-reports

py.test --junitxml=test-reports/TEST-UNIT-flask-app-medium.xml --cov-report term-missing --cov-report=html --cov application unit_tests
