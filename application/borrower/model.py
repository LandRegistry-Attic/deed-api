from application import db


class Borrower(db.Model):
    __tablename__ = 'borrower'

    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String, nullable=False)
    middlename = db.Column(db.String, nullable=True)
    surname = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=True)
    phonenumber = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self, id_):
        borrower = Borrower.query.filter_by(id=id_).first()

        if borrower is None:
            return borrower

        db.session.delete(borrower)
        db.session.commit()

        return borrower
