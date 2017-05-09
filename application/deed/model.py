import logging
import copy
import uuid
import os
from datetime import datetime
from builtins import FileNotFoundError

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.operators import and_

from application import db
from application.deed.utils import process_organisation_credentials
from application.deed.deed_status import DeedStatus
from application.deed.address_utils import format_address_string


LOGGER = logging.getLogger(__name__)


class Deed(db.Model):
    __tablename__ = 'deed'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    deed = db.Column(JSON)
    identity_checked = db.Column(db.String(1), nullable=False)

    status = db.Column(db.String(16), default='DRAFT')
    deed_xml = db.Column(db.LargeBinary, nullable=True)
    checksum = db.Column(db.Integer, nullable=True, default=-1)
    organisation_id = db.Column(db.String, nullable=True)
    organisation_name = db.Column(db.String, nullable=True)
    payload_json = db.Column(JSON)
    created_date = db.Column(db.DateTime, default=datetime.utcnow(),  nullable=False)

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_token():
        return str(uuid.uuid4())

    def get_json_doc(self):
        return copy.deepcopy(self.json_doc)

    def get_deed_status(title_number, mdref):

        deeds = Deed.query.filter(
            and_(
                Deed.deed['title_number'].astext == title_number,
                Deed.deed['md_ref'].astext == mdref
            )
        ).all()

        deeds_with_status = list(
            map(lambda deed: {
                "token": deed.token,
                "status": deed.status
            }, deeds)
        )

        return deeds_with_status

    def get_deeds_by_status(self, status):
        return Deed.query.filter(Deed.status.like(status), Deed.organisation_name != os.getenv('LR_ORGANISATION_NAME'),
                                 Deed.organisation_name.isnot(None)).count()

    def _get_deed_internal(self, deed_reference, organisation_id):
        if organisation_id != os.getenv('LR_ORGANISATION_ID'):
            LOGGER.debug("Internal request to view deed reference %s" % deed_reference)
            result = Deed.query.filter_by(token=str(deed_reference), organisation_id=organisation_id).first()
        else:
            result = Deed.query.filter_by(token=str(deed_reference)).first()

        return result

    def get_deed(self, deed_reference):
        conveyancer_credentials = process_organisation_credentials()
        organisation_id = conveyancer_credentials[os.getenv('DEED_CONVEYANCER_KEY')][1]

        return self._get_deed_internal(deed_reference, organisation_id)

    @staticmethod
    def get_signed_deeds():
        conveyancer_credentials = process_organisation_credentials()
        organisation_name = conveyancer_credentials[os.getenv('DEED_CONVEYANCER_KEY')][0]

        result = Deed.query.filter_by(organisation_name=organisation_name, status=DeedStatus.all_signed.value).all()

        all_signed_deeds = list(
            map(lambda deed: deed.token, result)
        )

        return all_signed_deeds

    def get_borrower_position(self, borrower_token):
        for idx, borrower in enumerate(self.deed['borrowers'], start=1):
            if borrower_token == str(borrower['token']).upper():
                return idx
        return -1


def deed_adapter(deed_reference):
    """
    An adapter for the deed to enhance and return in the required form.

    :param deed_reference:
    :return: The deed with status and token attributes set
    :rtype: deed
    """
    deed = Deed().get_deed(deed_reference)
    if deed is None:
        raise FileNotFoundError("There is no deed associated with deed id '{0}'.".format(deed_reference,))
    deed.deed['token'] = deed.token
    deed.deed['status'] = deed.status
    return deed


def deed_json_adapter(deed_reference):
    """
    An adapter for the deed to return as a dictionary for conversion to json.

    :param deed_reference:
    :return: The deed, as a dictionary.
    :rtype: dict
    """
    deed = deed_adapter(deed_reference)
    return {'deed': deed.deed}


def deed_pdf_adapter(deed_reference):
    """
    An adapter for the deed to return as a dictionary for conversion to json.

    :param deed_reference:
    :return: The deed, as a pdf.
    :rtype: pdf
    """
    deed_dict = deed_adapter(deed_reference).deed
    if 'effective_date' in deed_dict:
        temp = datetime.strptime(deed_dict['effective_date'], "%Y-%m-%d %H:%M:%S")
        deed_dict["effective_date"] = temp.strftime("%d/%m/%Y")
        deed_dict["effective_time"] = temp.strftime("%H:%M:%S")
    property_address = (deed_dict["property_address"])
    deed_dict["property_address"] = format_address_string(property_address)
    return deed_dict
