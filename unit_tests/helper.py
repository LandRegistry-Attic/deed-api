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
    deed_xml = "<dm-application xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http://localhost:9080/schemas/deed-schema-v0-2.xsd\">\
                <operativeDeed><deedData Id=\"deedData\"><titleNumber>GR515835</titleNumber><propertyDescription>5 The Drive, This Town, This County, PL4 4TH</propertyDescription>\
                <borrowers><borrower><name><privateIndividual><forename>Paul</forename><middlename>James</middlename><surname>Smythe</surname>\
                </privateIndividual></name><address>borrower address</address></borrower><borrower><name><privateIndividual><forename>Jane</forename><surname>Smythe</surname>\
                </privateIndividual></name><address>borrower address</address></borrower></borrowers><mdRef>e-MD12344</mdRef><chargeClause><creCode>CRE001</creCode>\
                <entryText>The borrower, with full title guarantee, charges to the lender the property by way of legal mortgage with payment of all money secured by this charge.</entryText>\
                </chargeClause><additionalProvisions><provision><code>addp001</code><entryText>This Mortgage Deed incorporates the &lt;a href=\'#\' rel=\'external\'&gt;Lenders Mortgage Conditions\
                 and Explanation 2006&lt;/a&gt;, a copy of which the borrower has received.</entryText><sequenceNumber>0</sequenceNumber></provision><provision><code>addp002</code>\
                 <entryText>The lender is obliged to make further advances and applies for the obligation to be entered in the register.</entryText>\
                 <sequenceNumber>1</sequenceNumber></provision><provision><code>addp003</code><entryText>The borrower applies to enter a restriction in the register that no disposition \
                 of the registered estate by the proprietor of the registered estate is to be registered without a written consent signed by the proprietor for the time being of the \
                 charge dated [the date of this charge] in favour of Bank of England Plc referred to in the charges register.</entryText><sequenceNumber>2</sequenceNumber>\
                 </provision></additionalProvisions><lender><organisationName><company><name>Bank of England Plc</name></company></organisationName>\
                 <address>12 Trinity Place, Regents Street, London NW10 6TQ</address><companyRegistrationDetails>Company registration number: 2347676</companyRegistrationDetails>\
                 </lender><effectiveClause>This charge takes effect when the registrar receives notification from Land Registry Devices that the charge is to take effect.</effectiveClause>\
                 </deedData><signatureSlots><borrower_signature><signature/><signatory><privateIndividual><forename>Paul</forename><middlename>James</middlename><surname>Smythe</surname>\
                 </privateIndividual></signatory></borrower_signature><borrower_signature><signature/><signatory><privateIndividual><forename>Jane</forename><surname>Smythe</surname>\
                 </privateIndividual></signatory></borrower_signature></signatureSlots></operativeDeed><effectiveDate></effectiveDate><authSignature/></dm-application>"


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
        "title_number": "GR515835",
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
    ]}
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
            "identity_checked": "Y",
            "title_no": "DN100",
            "organisation_locale": "gb",
            "organisation_name": "Land Registry Devices"
        },
        "service": "digital mortgage",
        "activity": "create deed"

    }
