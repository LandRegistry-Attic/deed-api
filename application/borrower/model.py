from application import db
import uuid

charset = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


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

    @staticmethod
    def generate_token():
        return generate_hex()

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

    def get_by_id(id_):
        return Borrower.query.filter_by(id=id_).first()

    def get_by_token(token_):
        return Borrower.query.filter_by(token=token_).first()


def bin_to_char(bin_str):
    pos = min(int(bin_str[:6], 2), len(charset)-1)
    return charset[pos]


def generate_hex():
    val = str(bin(uuid.uuid4().int))
    bin_str = val[2:]
    result = ""

    while len(bin_str) > 15:
        result += bin_to_char(bin_str[:15])
        bin_str = bin_str[15:]

    return result[:4]+"-"+result[-4:]
