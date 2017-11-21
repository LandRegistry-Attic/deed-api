import uuid
from sqlalchemy import not_, func, ForeignKey

from application import db

charset = list("0123456789ABCDEFGHJKLMNPQRSTUVXY")


class DatabaseException(Exception):
    pass


class BorrowerNotFoundException(Exception):
    pass


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
    signing_in_progress = db.Column(db.Boolean, nullable=True)

    @staticmethod
    def generate_token():
        return generate_hex()

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
        return Borrower.query.filter(func.upper(Borrower.token) == token_).first()

    def get_by_verify_pid(verify_pid):
        return Borrower.query.join(VerifyMatch).filter(VerifyMatch.verify_pid == verify_pid).first()

    def _get_borrower_internal(self, borrower_id):
        return Borrower.query.filter_by(id=borrower_id).first()

    def update_borrower_by_id(self, borrower):
        borrower_id = borrower["id"]

        existing_borrower = self._get_borrower_internal(borrower_id)

        if existing_borrower:

            existing_borrower.forename = borrower["forename"]
            existing_borrower.surname = borrower["surname"]
            existing_borrower.dob = borrower["dob"]
            existing_borrower.phonenumber = borrower["phone_number"]
            existing_borrower.address = borrower["address"]
            existing_borrower.gender = borrower["gender"]

            if 'middle_name' in borrower:
                existing_borrower.middlename = borrower["middle_name"]

            db.session.commit()

            return existing_borrower
        else:
            return "Error No Borrower"

    @staticmethod
    def update_borrower_signing_in_progress(borrower_token):
        borrower = Borrower.get_by_token(borrower_token)
        if borrower:
            borrower.signing_in_progress = True
            borrower.save()

            return True

        raise BorrowerNotFoundException

    def delete_borrowers_not_on_deed(self, ids, deed_reference):
        borrowers = self._get_borrowers_not_on_deed(ids, deed_reference)

        for borrower in borrowers:
            self._delete_borrower(borrower)

        return True

    def _get_borrowers_not_on_deed(self, ids, deed_reference):

        try:
            borrowers = Borrower.query.filter(not_(Borrower.id.in_(ids)), Borrower.deed_token == deed_reference).all()

            return borrowers
        except Exception as e:
            raise DatabaseException(e)

    def _delete_borrower(self, borrower):
        try:
            db.session.delete(borrower)
            db.session.commit()

            return True

        except Exception as e:
            raise DatabaseException(e)


class VerifyMatch(db.Model):
    __tablename__ = 'verify_match'

    verify_pid = db.Column(db.String, primary_key=True)
    borrower_id = db.Column(db.Integer, ForeignKey("borrower.id"), primary_key=True)
    confidence_level = db.Column(db.Integer, nullable=False)

    def remove_verify_match(self, pid_):
        try:
            match = VerifyMatch.query.filter_by(verify_pid=pid_).first()
            if match is None:
                return False

            db.session.delete(match)
            db.session.commit()
            return True

        except Exception as e:
            raise DatabaseException(e)


def bin_to_char(bin_str):
    # Converts 5 character binary string to a 2 digit integer. Then takes minimum between the 2 digit number and the lenght of the charset - 1.
    pos = min(int(bin_str[:5], 2), len(charset)-1)
    return charset[pos]  # Return character from charset based on position established above


def generate_hex():
    val = str(bin(uuid.uuid4().int))
    bin_str = val[2:]  # Remove 0b from beginning of string
    result = ""

    while len(bin_str) > 15:
        result += bin_to_char(bin_str[:15])
        bin_str = bin_str[15:]

    return result
