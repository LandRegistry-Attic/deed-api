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
source test.sh
```

## Acceptance tests

See, the following link for information on how to run the acceptance tests:-

[Acceptance Tests](https://github.com/LandRegistry/dm-acceptance-tests)

## Current Schema

The Deed requires a title number and at least 1 borrower

### Deed
The schema can be found below
```
https://github.com/LandRegistry/dm-deed-api/blob/develop/application/deed/schema.json
```
Example payload:
```
{
    "title_number": "DN100",
    "md_ref": "e-MD12344",
    "borrowers": [
        {
            "forename": "lisa",
            "middle_name": "ann",
            "surname": "bloggette",
            "address": "example address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154075"
        },
        {
            "forename": "frank",
            "middle_name": "ann",
            "surname": "bloggette",
            "address": "Example address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154076"
        }
    ]
}
```
