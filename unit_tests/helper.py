from application.deed.model import Deed


class DeedModelMock(Deed):
    token = "ABC1234"
    deed = {
        "title_number": "DN100",
        "md_ref": "e-MD12344",
        "property_address": "5 The Drive, This Town, This County, PL4 4TH",
        "borrowers": [
            {
                "forename": "lisa",
                "middle_name": "ann",
                "surname": "bloggette",
                "address": "test address with postcode, PL14 3JR",
                "token": "AAAAAA"
            },
            {
                "forename": "frank",
                "middle_name": "ann",
                "surname": "bloggette",
                "address": "Test Address With Postcode, PL14 3JR",
                "token": "BBBBBB"
            }
        ],
        "additional_provisions": [
            {
                "additional_provision_code": "addp001",
                "description": "Description"
            },
            {
                "additional_provision_code": "addp002",
                "description": "Description"
            }
        ],
        "charge_clause": {
            "cre_code": "CRE001",
            "description": "Description"
        },
        "lender": {
            "address": "Test Address, London NW10 7TQ",
            "name": "Bank of England Plc",
            "registration": "Company registration number: 123456"
        },
        "effective_clause": "Effective clause goes here",
        "identity_checked": "Y"
    }
    status = "DRAFT"


class MortgageDocMock:
    md_ref = "e-MD12121"
    data = '{"description":"test setup charge clause","lender":{ "name":"a new lender",' \
           '"address":"no 1 reputable street"}, "charge_clause": { "cre_code": "CRE001",' \
           '"description":"This is an example charge clause"}, "additional_provisions": ' \
           '[ { "additional_provision_code":"addp001", "description":"this is additional ' \
           'provision1"}, { "additional_provision_code":"addp002", "description":"this is ' \
           'additional provision2"}]}'


class DeedHelper:
    _json_doc = {
        "title_number": "DN100",
        "md_ref": "e-MD12344",
        "property_address": "5 The Drive, This Town, This County, PL4 4TH",
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
        "property_address": "5 The Drive, This Town, This County, PL4 4TH",
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
        ]
    }

    _invalid_phone_numbers = {"borrowers": [
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
    ]},
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
        ]
    }

    _validate_borrower = {"borrower_token": "aaaaaa", "dob": "23/01/1986", "phonenumber": "07502154999"}

    _validate_borrower_dob = {"borrower_token": "aaaaaa", "dob": "1/1/1986"}

    _invalid_blank_address = {
        "title_number": "DN100",
        "md_ref": "e-MD12344",
        "property_address": "",
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
        "identity_checked": "Y",
    }

    _add_borrower_signature = {"borrower_token": "3"}

    _verify_and_sign = {"borrower_token": "3",
                        "authentication_code": "aW23xw"}


class StatusMock:
    _status_with_mdref_and_titleno = [
        {
            "status": "DRAFT",
            "token": "c91d57"
        }
    ]

    _no_status_with_mdref_and_titleno = [
    ]


class AkumaMock:
    _approved_akuma_payload = {
        "payload": {
            "borrowers": [{
                "phone_number": "07502159062",
                "gender": "Male",
                "address": "2 The Street, Plymouth, PL1 2PP",
                "forename": "Paul",
                "dob": "22/03/1976",
                "middle_name": "James",
                "surname": "Smythe"
            }, {
                "phone_number": "07502154999",
                "gender": "Female",
                "address": "2 The Street, Plymouth, PL1 2PP",
                "dob": "01/12/1982",
                "surname": "Smythe",
                "forename": "Jane"
            }],
            "md_ref": "e-MD12344",
            "title_number": "DT107",
            "property_address": "5 The Drive, This Town, This County, PL4 4TH",
            "identity_checked": "Y",
            "title_no": "DT107",
            "organisation_locale": "gb",
            "organisation_name": "Land Registry Devices",
        },
        "service": "Digital Mortgage",
        "activity": "Create"

    }
