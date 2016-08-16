import logging
from application.deed.utils import process_organisation_credentials, validate_helper, valid_dob
from application.title_adaptor.service import TitleAdaptor
from flask import jsonify, abort
from flask.ext.api import status
from application.akuma.service import Akuma
from application.deed.service import valid_borrowers

LOGGER = logging.getLogger(__name__)


class Validation():
    def validate_organisation_credentials(self):
        """
        Get the conveyancer's credentials

        :type list: organisation_credentials
        :rtype: dict
        """
        organisation_credentials = process_organisation_credentials()

        if organisation_credentials:
            organisation_credentials = {'organisation_id': organisation_credentials["O"][1],
                                        'organisation_name': organisation_credentials["O"][0],
                                        'organisation_locale': organisation_credentials["C"][0]}
            return organisation_credentials


    def validate_payload(self, deed_json):
        error_count, error_message = validate_helper(deed_json)

        if error_count > 0:
            LOGGER.error("Schema validation 400_BAD_REQUEST")
            abort(status.HTTP_400_BAD_REQUEST, error_message)


    def  validate_title_number(self, deed_json):
        return_val = TitleAdaptor.do_check(deed_json['title_number'])
        if return_val != "title OK":
            error_message = jsonify({"message": return_val})
            abort(status.HTTP_400_BAD_REQUEST, error_message)


    def validate_borrower_names():
        return True

    def call_akuma(self, deed_json, deed_token, organisation_name, organisation_locale):
        check_result = Akuma.do_check(deed_json, "create_deed",
                                      organisation_name,
                                      organisation_locale, deed_token)
        LOGGER.info("Check ID: " + check_result['id'])


    def validate_dob(self, deed_json):
        borrowers = deed_json["borrowers"]

        valid = _(borrowers).chain()\
            .map(lambda x, *a: x['dob'])\
            .reduce(valid_dob, True).value()

        print ("Val", valid)
        return valid

    def validate_phonenumbers():
        return True

    def validate_md_ref():
        return True
