# dm-deed-api

The Deed API is a JSON API which stores deed objects.

This API holds the functionality for creating the migrating tables, getting data
from the database and putting a new JSON deed onto a database that returns an endpoint to that deed.

The API also holds the functionality to capture personal information provided and save it in a
separate table to be used at a later date for matching.

Please note that sensitive environment variables are inherited from the environment-store service and you
would need to bring it into your devenv config for these to be set.

### Contents

- [Usage](#usage)
- [Getting Started](#getting-started)
- [Migration](#migration)
- [Unit tests](#unit-tests)
- [Integration tests](#integration-tests)
- [Current Schema](#current-schema)

## Usage
```
get     /health                                 # Test endpoint for the application
get     /health/service-check                   # Check the health of all services connected to deed-api
get     /deed/<deed_reference>                  # Get a deed with an id in the URL
get     /dashboard/<status>                     # Gets the total amount of deeds for each status
get     /deed/retrieve-signed                   # Get all deeds that have been signed
post    /deed/                                  # Create a deed by posting a json object reflecting the schema
post    /deed/<deed_reference>/make-effective   # Makes a deed effective.
post    /deed/<deed_reference>/verify-auth-code # Verify the auth code provided by a borrower, for their prospective deed.
put     /deed/<deed_reference>                  # Update a deed. A new id is generated unless the id field is present in the payload
delete  /borrowers/delete/<borrower_id>         # delete a borrower from the borrower table
```

## Getting Started

1. Clone the repo
2. In the directory enter the command
```
pip install -r requirements.txt
```
3. To run the application run the command
```
source run.sh
```

## Migration

Run the Migration
```
python manage.py db upgrade
```

Add a migration

```
python manage.py db revision --autogenerate
```

> For some helpful documentation on using alembic go [here](alembic.md)

## Unit tests

Run the unit tests

```
source unit_test.sh
```
If you get the following errors:
```
Command "python setup.py egg_info" failed with error code 1 in /private/var/folders/7c/lgmjhvmj5f3f0dvgk01ygzz80000gq/T/pip-build-c5k5vmpa/psycopg2/
```
then install (on a Mac)
```
brew install postgresql
```

```
OSError: dlopen() failed to load a library: cairo / cairo-2
```
then install (on a Mac)
```
brew install python cairo pango gdk-pixbuf libxml2 libxslt libffi
```

## Integration tests

```
source integration_tests.sh
```

## Current Schema

The Deed requires a title number, md ref and at least 1 borrower

### Deed
The schema can be found in the application/deed/schemas folder under the filename of deed-api

Example payload with Enact-style lender-reference, date of mortgage offer, miscellaneous information:

```
{
	"title_number": "CYM123457",
	"md_ref": "e-MD1291A",
	"property_address": "0 The Drive, This Town, This County, PL0 0TH",
	"borrowers": [{
		"forename": "Ann",
		"surname": "Smith",
		"gender": "Male",
		"address": "test address with postcode, PL0 0JR",
		"dob": "02/02/1922",
		"phone_number": "07777777777"
	}],
	"identity_checked": "Y",
	"date_of_mortgage_offer": "a date string",
	"miscellaneous_information": "A Conveyancer"
}
```

Validate borrower

```
curl -X POST -d '{"borrower_token":"AHDHDI", "dob":"02/02/1922"}' -H "Content-Type:application/json" localhost:9020/borrower/validate
```
