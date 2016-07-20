from application.deed.utils import validate_helper
from application.title_adaptor.service import TitleAdaptor
from application.deed.validate_borrowers import check_borrower_names, BorrowerNamesException
import logging
from flask.ext.api import status
from flask import jsonify

LOGGER = logging.getLogger(__name__)

def deed_validator(deed):

    error_count, error_message = validate_helper(deed)

    if error_count > 0:
        LOGGER.error("Schema validation 400_BAD_REQUEST")
        return error_message, status.HTTP_400_BAD_REQUEST

    valid_title = TitleAdaptor.do_check(deed['title_number'])

    if valid_title != "title OK":
        return jsonify({"message": valid_title}), status.HTTP_400_BAD_REQUEST

    try:
        check_borrower_names(deed)

    except BorrowerNamesException:
        return (jsonify({'message':
                        "a digital mortgage cannot be created as there is a discrepancy between the names given and those held on the register."}),
                        status.HTTP_400_BAD_REQUEST)

    return "passed", status.HTTP_200_OK
