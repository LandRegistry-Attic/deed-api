# Intended for use by unit tests, to check that aspects of the deed are being rendered when they are present

complete_deed_dict = {
    "additional_provisions": [
        {
            "additional_provision_code": "addp001",
            "description": "The borrower acknowledges receipt of the advance specified in the offer."
        },
        {
            "additional_provision_code": "addp002",
            "description": "This mortgage deed incorporates the Mortgage Conditions (Issue 'J') which have been \
                laid down by the Board of Directors of the lender and of which a copy has been supplied to the \
                borrower."
        },
        {
            "additional_provision_code": "addp003",
            "description": "This mortgage deed is made for securing further advances (including re-advances)."
        },
        {
            "additional_provision_code": "addp004",
            "description": "The borrower as a member of the Test Building Society will during the existence \
                of this mortgage deed be bound by the Rules of the Society in force from time to time including rules \
                adopted and amendments made after the date of this mortgage deed, except insofar as the Rules are \
                expressly modified by the Mortgage Conditions and this mortgage deed."
        },
        {
            "additional_provision_code": "addp005",
            "description": "The borrower applies to the Chief Land Registrar to enter the following restriction \
                in the Proprietorship Register of the property: &quot;No disposition of the registered estate by the \
                proprietor of the registered estate or by the proprietor of any registered charge, not being a charge \
                registered before the entry of this restriction, is to be registered without a written consent signed \
                by the proprietor for the time being of the charge dated [the date of this charge] in favour of \
                Test Building Society referred to in the Charges Register&quot;."
        }
    ],
    "borrowers": [
        {
            "forename": "Julius",
            "id": 196,
            "middle_name": "Hill",
            "signature": "13 March 2017 12:44PM",
            "surname": "North",
            "token": "T8A4LBL8"
        },
        {
            "forename": "Mr Dillan",
            "id": 197,
            "middle_name": "Ale",
            "signature": "13 March 2017 12:45PM",
            "surname": "Jives",
            "token": "LF44UML2"
        }
    ],
    "charge_clause": {
        "cre_code": "CRE001",
        "description": "The borrower, with full title guarantee, charges to the lender the property by way of \
            legal mortgage with payment of all money secured by the charge."
    },
    "date_of_mortgage_offer_details": {
        "date_of_mortgage_offer_heading": "Date of Mortgage Offer",
        "date_of_mortgage_offer_value": "a date string"
    },
    "effective_clause": "This Charge takes effect when the registrar receives notification from Test Organisation \
        that the Charge is to take effect.",
    "lender": {
        "address": "Test House PO Box 0, Test Street CV0 0QN",
        "name": "TEST BUILDING SOCIETY",
        "registration": ""
    },
    "md_ref": "e-MD1291A",
    "miscellaneous_information_details": {
        "miscellaneous_information_heading": "Your conveyancer contact is",
        "miscellaneous_information_value": "bob test"
    },
    "property_address": "0 The Drive, This Town, This County, PL0 0TH",
    "reference_details": {
        "lender_reference_name": "Test reference",
        "lender_reference_value": "123"
    },
    "status": "ALL-SIGNED",
    "title_number": "WYK722599",
    "token": "c499a0a9-c675-4d40-8c0e-9a4cf49ef3dc"

}
