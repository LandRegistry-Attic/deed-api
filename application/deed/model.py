from application import db
from sqlalchemy.dialects.postgresql import JSON
import copy
import uuid


class Deed(db.Model):
    __tablename__ = 'deed'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String, nullable=False)
    deed = db.Column(JSON)

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_token():
        return str(uuid.uuid4().hex[:6]).lower()

    def get_json_doc(self):
        return copy.deepcopy(self.json_doc)
