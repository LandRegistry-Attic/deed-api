from application import db


class NAAAudit(db.Model):
    __tablename__ = 'naa_audit'

    id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, nullable=False)
    date_accepted = db.Column(db.DateTime, nullable=False)

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()
