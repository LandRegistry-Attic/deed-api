from application import db
from sqlalchemy.dialects.postgresql import JSON


class MortgageDocument(db.Model):
    __tablename__ = 'mortgage_document'

    md_ref = db.Column(db.String, primary_key=True)
    data = db.Column(JSON)
    legal_warning = db.Column(db.String, nullable=True)

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    def get_by_md(md_):
        return MortgageDocument.query.filter_by(md_ref=md_).first()
