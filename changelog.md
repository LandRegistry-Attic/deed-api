# Changelog

### Baseline 27-04-2017

#### Whats New
None

#### Network Changes
None

#### Environment Variables
ACCOUNT_SID:                     'ACfcfc375748835920eb4ec115bfa3008f'
AKUMA_ADDRESS:                   Set to point to ip address of Akuma stub in AWS or matching AKUMA environment if applicable
AUTH_TOKEN:                      '52e3b53a462f3f184f50d90816c43e64'
DEED_CONVEYANCER_KEY:            'O'                                                                                           # The values for this key are specified in the webseal headers. Provides the ability to access organisation name and id
DEED_DATABASE_URI:               Set to connection string of deed database for appropriate region
DEED_WEBSEAL_LOCALE:             'C'                                                                                           # The key used to access the webseal headers locale
ESEC_CLIENT_URI:                 set to ip address abd port of esec-client in same region IL2
LR_HEADER_INTERNAL_ORG:          'X-Land-Registry'                                                                             # Land Registry's internal organisation name for deed-api
LR_ORGANISATION_ID:              '*'                                                                                           # The organisation id used for retrieving internal deeds
LR_ORGANISATION_NAME:            'Land Registry Devices'                                                                       # The organisation name we use for test purposes; we exclude results including this name from actual database related calls
ORGANISATION_API_ADDRESS:        Set to ip address of organisation-api in same region
REGISTER_ADAPTER:                Set to ip address of register-adapter in same region
TITLE_ADAPTOR_URI:               Set to ip address of title-adapter-api in same region
TWILIO_PHONE_NUMBER:             '+441442796219'
WEBSEAL_HEADER_INT_INTERNAL:     'CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Test2,O=*,C=gb'          # Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_INT_ORGANISATION: 'CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Test%20Organisation,O=1000.1.2,C=gb'       # Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_INT_TEST_2:       'CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Test,O=1360,C=gb'        # Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_INT_TEST_3:       'CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20TestD,O=1362.5.1,C=gb'   # Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_INT_TEST_4:       'CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=testusers,O=1359.2.1,C=gb'                 # Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_KEY:              'Iv-User-L'                                                                                   # Fake webseal header key - to hit deed-api
WEBSEAL_HEADER_VALUE:            'CN=DigitalMortgage%20DigitalMortgage,OU=devices,O=Land%20Registry%20Devices,O=1359.2.1,C=gb' # Fake webseal header value - to hit deed-api
