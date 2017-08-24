valid_deed = {
    "title_number": "CYM123457",
    "md_ref": "e-MD12344",
    "property_address": "0 The Drive, This Town, This County, PL0 0TH",
    "identity_checked": "Y",
    "borrowers": [
        {
            "forename": "Ann",
            "surname": "Smith",
            "gender": "Female",
            "address": "test address with postcode, PL0 0JR",
            "dob": "02/02/1922",
            "phone_number": "07777777777"
        }
    ]
}

valid_deed_with_reference = {
    "title_number": "CYM123457",
    "md_ref": "e-MD1291A",
    "property_address": "0 The Drive, This Town, This County, PL0 0TH",
    "identity_checked": "Y",
    "borrowers": [
        {
            "forename": "Ann",
            "surname": "Smith",
            "gender": "Female",
            "address": "test address with postcode, PL0 0JR",
            "dob": "02/02/1922",
            "phone_number": "07777777777"
        }
    ],
    "reference": "test"
}

valid_deed_with_date_of_mortgage_offer = {
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
    "reference": "123",
    "date_of_mortgage_offer": "a date string"
}

valid_deed_with_deed_effector = {
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
    "reference": "123",
    "date_of_mortgage_offer": "a date string",
    "deed_effector": "A Conveyancer"
}

new_deed = {
    "title_number": "CYM123457",
    "md_ref": "e-MD12344",
    "property_address": "0 The Drive, This Town, This County, PL0 0TH",
    "identity_checked": "Y",
    "borrowers": [
        {
            "forename": "Ann",
            "surname": "Smith",
            "gender": "Female",
            "address": "test address with postcode, PL0 0JR",
            "dob": "02/02/1922",
            "phone_number": "07777777777"
        }
    ]
}

valid_deed_two_borrowers = {
    "title_number": "GR515835",
    "md_ref": "e-MD12344",
    "property_address": "0 The Drive, This Town, This County, PL0 0TH",
    "identity_checked": "Y",
    "borrowers": [
        {
            "forename": "Ann",
            "surname": "Smith",
            "gender": "Female",
            "address": "test address with postcode, PL0 0JR",
            "dob": "02/02/1922",
            "phone_number": "07777777776"
        },
        {
            "forename": "Fredd",
            "surname": "Smith",
            "gender": "Male",
            "address": "test address with postcode, PL0 0JR",
            "dob": "02/02/1922",
            "phone_number": "07777777777"
        }
    ]
}
