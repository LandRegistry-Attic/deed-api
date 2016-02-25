import requests
import logging
from application import config
from flask.ext.api import status
from flask import abort

LOGGER = logging.getLogger(__name__)

def add_borrower_signature(deed_xml, borrower_pos):  # pragma: no cover
    data = None
    LOGGER.info("Calling dm-esec-client")
    request_url = config.ESEC_CLIENT_BASE_HOST + '/esec/add_borrower_signature/' + str(borrower_pos)
    element_id = 'deedData'
    borrower_path = "dm-application/operativeDeed/signatureSlots"

    parameters = {'element-id':element_id, 'borrowers-path':borrower_path}

    resp = requests.post(request_url, params=parameters, data=deed_xml)

    if resp.status_code == status.HTTP_200_OK:
        LOGGER.info("Response XML = %s" % resp.content)
        return resp.content, resp.status_code
    else:
        LOGGER.error("Esecurity Client Exception")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)