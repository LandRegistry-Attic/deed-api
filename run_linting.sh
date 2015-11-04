### Retrieve the current location the script is running
currentLocation="$(cd "$(dirname "$0")"; pwd)"
echo currentLocation

flake8 $currentLocation

exit $?
