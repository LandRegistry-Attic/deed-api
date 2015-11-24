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
get     /health                     # test endpoint for the application
get     /deed/<id_>                 # get a deed with an id in the URL
post    /deed/                       # Create a deed by posting a json object reflecting the schema

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

```
{
 "definitions": {
     "title_number": {
       "pattern": "^([A-Z]{0,3}[1-9][0-9]{0,5}|[0-9]{1,6}[ZT])$",
       "type": "string"
     },
   "PrivateIndividualName": {
           "type": "object",
           "properties": {
               "surname": {
                   "type": "string"
               },
               "forename": {
                   "type": "string"
               },
               "middle_name": {
                   "type": "string"
               },
               "dob": {
                 "type": "string",
                 "pattern": "^(0?[1-9]|[12][0-9]|3[01])[\\/\\-](0?[1-9]|1[012])[\/\\-]\\d{4}$"
               },
               "gender": {
                 "type": "string",
                 "pattern": "^[MFU]{1}"
               },
             "phone_number": {
               "type": "string",
               "pattern": "^(07[\\d]{8,12}|447[\\d]{7,11})$"
             },
           "address":{
                 "type": "string",
                 "pattern": "(GIR 0AA|[A-PR-UWYZ]([0-9][0-9A-HJKPS-UW]?|[A-HK-Y][0-9][0-9ABEHMNPRV-Y]?) [0-9][ABD-HJLNP-UW-Z]{2})"
               }
           },
           "required": [
               "surname","forename", "dob", "phone_number", "address"
           ],
           "additionalProperties": false
       }
  },
  "properties": {
    "title_number": {
      "$ref": "#/definitions/title_number"
    },
    "borrowers":{
      "type": "array",
      "minItems": 1,
      "items": [
        {
          "type": "object",
          "$ref": "#/definitions/PrivateIndividualName"
        }
      ]
    }
  },
  "required": ["title_number", "borrowers"],
  "type": "object",
  "additionalProperties": false
}
```

e.g.
```
{
    "title_number": "DN100",
    "borrowers": [
        {
            "forename": "lisa",
            "middle_name": "ann",
            "surname": "bloggette",
            "address": "example address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154062"
        },
        {
            "forename": "frank",
            "middle_name": "ann",
            "surname": "bloggette",
            "address": "Example address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154062"
        }
    ]
}
```
