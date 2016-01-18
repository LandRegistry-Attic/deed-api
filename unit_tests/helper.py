class DeedModelMock:
    token = "ABC1234"
    deed = {"title_number": "DN100"}


class MortgageDocMock:
    md_ref = "MD12121"
    data = '{"description":"test setup charge clause","lender":{ "name":"a new lender",' \
           '"address":"no 1 reputable street"}, "charge_clauses": [ { "cre_code": "CRE001",' \
           '"description":"This is an example charge clause"}], "additional_provisions": ' \
           '[ { "additional_provision_code":"addp001", "description":"this is additional ' \
           'provision1"}, { "additional_provision_code":"addp002", "description":"this is ' \
           'additional provision2"}]}'


class DeedHelper:
    _json_doc = {
        "title_number": "DN100",
        "md_ref": "e-MD12344",
        "borrowers": [
            {
                "forename": "lisa",
                "middle_name": "ann",
                "surname": "bloggette",
                "gender": "Male",
                "address": "test address with postcode, PL14 3JR",
                "dob": "23/01/1986",
                "phone_number": "07502154062"
            },
            {
                "forename": "frank",
                "middle_name": "ann",
                "surname": "bloggette",
                "gender": "Female",
                "address": "Test Address With Postcode, PL14 3JR",
                "dob": "23/01/1986",
                "phone_number": "07502154061"
            }
        ],
        "identity_checked": "Y"
    }

    _invalid_title = {
        "title_number": "BBBB12313212BB",
        "md_ref": "mortgageref",
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
        ],
        "identity_checked": "Y"
    }

    _valid_borrowers = {
        "borrowers": [
            {
                "forename": "lisa",
                "middle_name": "ann",
                "surname": "bloggette",
                "gender": "M",
                "address": "test address with postcode, PL14 3JR",
                "dob": "23/01/1986",
                "phone_number": "07502154062"
            },
            {
                "forename": "frank",
                "middle_name": "ann",
                "surname": "bloggette",
                "gender": "M",
                "address": "Test Address With Postcode, PL14 3JR",
                "dob": "23/01/1986",
                "phone_number": "07502154061"
            }
        ],
        "identity_checked": "Y"
    }

    _invalid_phone_numbers = {
        "borrowers":
            [
                {
                    "forename": "lisa",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "M",
                    "address": "test address with postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154062"
                },
                {
                    "forename": "frank",
                    "middle_name": "ann",
                    "surname": "bloggette",
                    "gender": "M",
                    "address": "Test Address With Postcode, PL14 3JR",
                    "dob": "23/01/1986",
                    "phone_number": "07502154062"
                }
            ],
            "identity_checked": "Y"
        }

    _invalid_blanks_on_required_fields = {
        "borrowers": [
            {
                "forename": "lisa",
                "middle_name": "ann",
                "surname": "",
                "gender": "M",
                "address": "test address with postcode, PL14 3JR",
                "dob": "23/01/1986",
                "phone_number": "07502154062"
            },
            {
                "forename": "",
                "middle_name": "ann",
                "surname": "bloggette",
                "gender": "M",
                "address": "Test Address With Postcode, PL14 3JR",
                "dob": "23/01/1986",
                "phone_number": "07502154061"
            }
        ],
        "identity_checked": "Y"
    }
