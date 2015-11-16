class DeedModelMock:
    id = 1
    deed = {"deed": {"title_number": "DN100", "id": 1}}


class DeedHelper:
    _json_doc = {
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

    _invalid_title = {
        "title_number": "BBBB12313212BB",
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
