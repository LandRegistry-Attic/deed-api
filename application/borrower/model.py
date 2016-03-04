from application import db
import uuid


class Borrower(db.Model):
    __tablename__ = 'borrower'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    deed_token = db.Column(db.String, nullable=False)
    forename = db.Column(db.String, nullable=False)
    middlename = db.Column(db.String, nullable=True)
    surname = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=True)
    phonenumber = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    esec_user_name = db.Column(db.String, nullable=True)

    @staticmethod
    def generate_token():
        return str(uuid.uuid4().hex[:6]).lower()

    def save(self):  # pragma: no cover
        db.session.add(self)
        db.session.commit()

    def delete(self, id_):  # pragma: no cover
        borrower = Borrower.query.filter_by(id=id_).first()

        if borrower is None:
            return borrower

        db.session.delete(borrower)
        db.session.commit()

        return borrower

    def get_by_id(id_):
        return Borrower.query.filter_by(id=id_).first()

    def get_by_token(token_):
        return Borrower.query.filter_by(token=token_).first()
