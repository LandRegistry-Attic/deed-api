import copy
import uuid
from application import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.operators import and_


class Deed(db.Model):
    __tablename__ = 'deed'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    deed = db.Column(JSON)
    identity_checked = db.Column(db.String(1), nullable=False)
    status = db.Column(db.String(16), default='CREATED')

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_token():
        return str(uuid.uuid4().hex[:6]).lower()

    def get_json_doc(self):
        return copy.deepcopy(self.json_doc)
