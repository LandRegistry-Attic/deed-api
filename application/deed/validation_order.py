import logging
from application.deed.utils import process_organisation_credentials, validate_helper, valid_dob, is_unique_list
from application.title_adaptor.service import TitleAdaptor
from application.akuma.service import Akuma
from application.deed.validate_borrowers import check_borrower_names, BorrowerNamesException
from underscore import _
from application.mortgage_document.model import MortgageDocument

LOGGER = logging.getLogger(__name__)


class Validation():
    def validate_organisation_credentials(self):
        """
        Get the conveyancer's credentials

        :type list: organisation_credentials
        :rtype: dict
        """
        organisation_credentials = process_organisation_credentials()

        if organisation_credentials is not None:
            organisation_credentials = {'organisation_id': organisation_credentials["O"][1],
                                        'organisation_name': organisation_credentials["O"][0],
                                        'organisation_locale': organisation_credentials["C"][0]}
            return organisation_credentials
        else:
            LOGGER.error("Unable to process organisation credentials")
            return None

    def validate_payload(self, deed_json):
        error_count, error_message = validate_helper(deed_json)
        LOGGER.error("Schema validation 400_BAD_REQUEST")
        return error_count, error_message

    def validate_title_number(self, deed_json):
        return_val = TitleAdaptor.do_check(deed_json['title_number'])
        if return_val != "title OK":
            LOGGER.error("Title Validation Error: " + str(return_val))
        return return_val

    def validate_borrower_names(self, deed_json):
        try:
            check_borrower_names(deed_json)
            return True, ""

        except BorrowerNamesException:
            msg = "a digital mortgage cannot be created as there is a discrepancy between the names given and those held on the register."
            return False, msg

    def call_akuma(self, deed_json, deed_token, organisation_name, organisation_locale, deed_type):
        check_result = Akuma.do_check(deed_json, deed_type,
                                      organisation_name,
                                      organisation_locale, deed_token)
        if deed_type == "create deed":
            LOGGER.info("Check ID: " + check_result['id'])
        elif deed_type == "modify deed":
            LOGGER.info("Check ID - MODIFY: " + check_result['id'])

        return check_result

    def validate_dob(self, deed_json):
        borrowers = deed_json["borrowers"]

        valid = _(borrowers).chain()\
            .map(lambda x, *a: x['dob'])\
            .reduce(valid_dob, True).value()

        if not valid:
            msg = "Date of birth must not be a date in the future"
            LOGGER.error(msg)
            return valid, msg
        else:
            return True, ""

    def validate_phonenumbers(self, deed_json):
        borrowers = deed_json["borrowers"]

        phone_number_list = _(borrowers).chain()\
            .map(lambda x, *a: x['phone_number'])\
            .value()

        valid = is_unique_list(phone_number_list)

        if not valid:
            msg = "A mobile phone number must be unique to an individual"
            LOGGER.error(msg)
            return valid, msg
        else:
            return True, ""

    def validate_md_exists(self, md_ref):
        try:
            mortgage_document = MortgageDocument.query.filter_by(md_ref=str(md_ref)).first()
        except Exception as e:
            LOGGER.error("Database Exception - %s" % e)

        if mortgage_document is None:
            msg = "mortgage document associated with supplied md_ref is not found"
            LOGGER.error(msg)
            return False, msg
