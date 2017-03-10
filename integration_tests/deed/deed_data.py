valid_deed = {
    "title_number": "CYM123457",
    "md_ref": "e-MD12344",
    "property_address": "5 The Drive, This Town, This County, PL4 4TH",
    "identity_checked": "Y",
    "borrowers": [
        {
            "forename": "Ann",
            "surname": "Smith",
            "gender": "Female",
            "address": "test address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154062"
        }
    ]
}

valid_deed_with_reference = {
    "title_number": "CYM123457",
    "md_ref": "e-MD1291A",
    "property_address": "5 The Drive, This Town, This County, PL4 4TH",
    "identity_checked": "Y",
    "borrowers": [
        {
            "forename": "Ann",
            "surname": "Smith",
            "gender": "Female",
            "address": "test address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154062"
        }
    ],
    "reference": "test"
}

valid_deed_with_date_of_mortgage_offer = {
    "title_number": "CYM123457",
    "md_ref": "e-MD1291A",
    "property_address": "5 The Drive, This Town, This County, PL4 4TH",
    "borrowers": [{
        "forename": "Ann",
        "surname": "Smith",
        "gender": "Male",
        "address": "test address with postcode, PL14 3JR",
        "dob": "23/01/1987",
        "phone_number": "07502154069"
    }],
    "identity_checked": "Y",
    "reference": "123",
    "date_of_mortgage_offer": "a date string",
    "miscellaneous_information": "A Conveyancer"
}

valid_deed_with_miscellaneous_info = {
    "title_number": "CYM123457",
    "md_ref": "e-MD1291A",
    "property_address": "5 The Drive, This Town, This County, PL4 4TH",
    "borrowers": [{
        "forename": "Ann",
        "surname": "Smith",
        "gender": "Male",
        "address": "test address with postcode, PL14 3JR",
        "dob": "23/01/1987",
        "phone_number": "07502154069"
    }],
    "identity_checked": "Y",
    "reference": "123",
    "date_of_mortgage_offer": "a date string",
    "miscellaneous_information": "A Conveyancer"
}

new_deed = {
    "title_number": "CYM123457",
    "md_ref": "e-MD12344",
    "property_address": "6 The Drive, This Town, This County, PL4 4TH",
    "identity_checked": "Y",
    "borrowers": [
        {
            "forename": "Ann",
            "surname": "Smith",
            "gender": "Female",
            "address": "test address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154062"
        }
    ]
}

valid_deed_two_borrowers = {
    "title_number": "GR515835",
    "md_ref": "e-MD12344",
    "property_address": "5 The Drive, This Town, This County, PL4 4TH",
    "identity_checked": "Y",
    "borrowers": [
        {
            "forename": "Ann",
            "surname": "Smith",
            "gender": "Female",
            "address": "test address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07502154062"
        },
        {
            "forename": "Fredd",
            "surname": "Smith",
            "gender": "Male",
            "address": "test address with postcode, PL14 3JR",
            "dob": "23/01/1986",
            "phone_number": "07584040376"
        }
    ]
}
