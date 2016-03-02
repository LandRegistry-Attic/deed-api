from application import db
from sqlalchemy.dialects.postgresql import JSON


class MortgageDocument(db.Model):
    __tablename__ = 'mortgage_document'

    md_ref = db.Column(db.String, primary_key=True)
    data = db.Column(JSON)

    def save(self): # pragma: no cover
        db.session.add(self)
        db.session.commit()
