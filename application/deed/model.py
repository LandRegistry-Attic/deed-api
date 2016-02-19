import copy
import uuid
from application import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.operators import and_
from application.deed.utils import process_organisation_credentials


class Deed(db.Model):
    __tablename__ = 'deed'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    deed = db.Column(JSON)
    identity_checked = db.Column(db.String(1), nullable=False)
    status = db.Column(db.String(16), default='DRAFT')
    organisation_id = db.Column(db.String, nullable=True)
    organisation_name = db.Column(db.String, nullable=True)

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_token():
        return str(uuid.uuid4().hex[:6]).lower()

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

    @staticmethod
    def get_deed(deed_reference):

        conveyancer_credentials = process_organisation_credentials()
        organisation_id = conveyancer_credentials["O"][1]

        result = Deed.query.filter_by(token=str(deed_reference), organisation_id=organisation_id).first()

        return result