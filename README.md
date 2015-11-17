# dm-deed-api

The Deed API is a JSON API which stores deed objects.

This API holds the functionality for creating the migrating tables, getting data
from the database, converting to JSON and returns as an endpoint.

### Contents

- [Usage](#usage)
- [Getting Started](#getting-started)
- [Changing the migration](#changing-the-migration)
- [Current Schema](#current-schema)

## Usage
```
get     /health                     # test endpoint for the application
get     /deed/<id_>                 # get a deed with an id in the URL
post    /deed                       # Create a deed by posting a json object reflecting the schema

```
> [schema](#current-schema) for post

## Getting Started
1. Clone the repo
2. In the directory enter the command
```
pip install -r requirements.txt
```

3. Export your database URI
```
export DATABASE_URI=postgresql://username:password@localhost/database
```

4. To run the migration run the command
```
python manage.py db upgrade head
```

5. To run the application run the command
```
source run.sh
```

## Changing the migration
All you have to do is change/create the related model and run the command

```
python manage.py db revision --autogenerate
```

> For some helpful documentation on using alembic go [here](alembic.md)

## Current Schema

The Deed requires a title_number and at least 1 borrower

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
               }
           },
           "required": [
               "surname","forename"
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
            "forename": "fred",
            "middle_name": "joe",
            "surname": "bloggs"
        },
        {
            "forename": "lisa",
            "surname": "bloggette"
        }
    ]
}
```
