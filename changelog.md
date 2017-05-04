# Changelog

### Baseline 27-04-2017

#### Whats New
None

#### Network Changes
None

#### Environment Variables
ACCOUNT_SID:                     test info
AKUMA_ADDRESS:                   Set to point to ip address of Akuma stub in AWS or matching AKUMA environment if applicable
AUTH_TOKEN:                      test info
DEED_CONVEYANCER_KEY:            The values for this key are specified in the webseal headers. Provides the ability to access organisation name and id
DEED_DATABASE_URI:               Set to connection string of deed database for appropriate region
DEED_WEBSEAL_LOCALE:             The key used to access the webseal headers locale
ESEC_CLIENT_URI:                 set to ip address abd port of esec-client in same region IL2
LR_HEADER_INTERNAL_ORG:          Land Registry's internal organisation name for deed-api
LR_ORGANISATION_ID:              The organisation id used for retrieving internal deeds
LR_ORGANISATION_NAME:            The organisation name we use for test purposes; we exclude results including this name from actual database related calls
ORGANISATION_API_ADDRESS:        Set to ip address of organisation-api in same region
REGISTER_ADAPTER:                Set to ip address of register-adapter in same region
TITLE_ADAPTOR_URI:               Set to ip address of title-adapter-api in same region
TWILIO_PHONE_NUMBER:             Test phone number
WEBSEAL_HEADER_INT_INTERNAL:     Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_INT_ORGANISATION: Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_INT_TEST_2:       Fake webseal header value - used in Integration tests
WqEBSEAL_HEADER_INT_TEST_3:       Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_INT_TEST_4:       Fake webseal header value - used in Integration tests
WEBSEAL_HEADER_KEY:              Fake webseal header key - to hit deed-api
WEBSEAL_HEADER_VALUE:            Fake webseal header value - to hit deed-api
