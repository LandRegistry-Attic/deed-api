# dm-deed-api

The Deed API is a JSON API which stores deed objects.

This API holds the functionality for creating the migrating tables, getting data
from the database and putting a new JSON deed onto a database that returns an endpoint to that deed.

The API also holds the functionality to capture personal information provided and save it in a
separate table to be used at a later date for matching.

### Contents

- [Usage](#usage)
- [Getting Started](#getting-started)
- [Migration](#migration)
- [Unit tests](#unit-tests)
- [Acceptance tests](#acceptance-tests)
- [Current Schema](#current-schema)

## Usage
```
get     /health                          # test endpoint for the application
get     /deed/<id_>                      # get a deed with an id in the URL
post    /deed/                           # Create a deed by posting a json object reflecting the schema
delete  /borrowers/delete/<borrower_id>  # delete a borrower from the borrower table

```
> [schema](#current-schema) for post

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

## Acceptance tests

See, the following link for information on how to run the acceptance tests:-

[Acceptance Tests](https://192.168.249.38/digital-mortgage/acceptance-tests)

## Current Schema

The Deed requires a title number and at least 1 borrower

### Deed
The schema can be found below
```
https://192.168.249.38/digital-mortgage/deed-api/blob/develop/application/deed/schema.json
```
Example payload:
```
{
    "title_number": "DT100",
    "md_ref": "e-MD12344",
    "borrowers": [
      {
           "forename": "Paul",
           "middle_name": "James",
           "surname": "Smythe",
           "gender": "Male",
           "address": "2 The Street, Plymouth, PL1 2PP",
           "dob": "01/10/1976",
           "phone_number": "07502159062"
       },
       {
            "forename": "Jane",
            "surname": "Smythe",
            "gender": "Female",
            "address": "2 The Street, Plymouth, PL1 2PP",
            "dob": "01/12/1982",
            "phone_number": "07502154999"
        }
    ],
    "identity_checked": "Y",
    "property_address": "5 The Drive, This Town, This County, PL4 4TH"
}
```

# Useful curl commands

Add deed

```
curl -i -X POST localhost:9020/deed/ \
-H "Content-Type:application/json"  \
-H "Iv-User-L:CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Devices,O=1359.2.1,C=gb"  \
-d @- << EOF
{
    "title_number": "GR515835",
    "md_ref": "e-MD12344",
    "borrowers": [
      {
           "forename": "Barry",
           "surname": "Jones",
           "gender": "Male",
           "address": "2 The Street, Plymouth, PL1 2PP",
           "dob": "01/10/1976",
           "phone_number": "07502159062"
       }
    ],
    "identity_checked": "Y",
    "property_address": "5 The Drive, This Town, This County, PL4 4TH"
}
EOF
```

Validate borrower

```
curl -X POST -d '{"borrower_token":"AHDHDI", "dob":"13/05/79"}' -H "Content-Type:application/json" localhost:9020/borrower/validate
```
