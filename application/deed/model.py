import copy
import uuid
import json
from application import db
from sqlalchemy.dialects.postgresql import JSON
from application.mortgage_document.model import MortgageDocument
from flask import abort
from flask.ext.api import status
import logger

LOGGER = logger.get_logger(__name__)


class Deed(db.Model):
    __tablename__ = 'deed'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    deed = db.Column(JSON)
    identity_checked = db.Column(db.String(1), nullable=False)

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_token():
        return str(uuid.uuid4().hex[:6]).lower()

    def get_json_doc(self):
        return copy.deepcopy(self.json_doc)

    def add_clauses(self):
        md_ref = self.deed["md_ref"]
        mortgage_document = MortgageDocument.query.filter_by(md_ref=str(md_ref)).first()
        if mortgage_document is not None:
            md_json = json.loads(mortgage_document.data)
            self.deed["charge_clauses"] = md_json["charge_clauses"]
            self.deed["additional_provisions"] = md_json["additional_provisions"]
            self.deed["lender"] = md_json["lender"]
        else:
            LOGGER.error("mortgage document associated md_ref not found")
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
