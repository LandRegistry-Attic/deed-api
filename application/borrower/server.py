from application.borrower.model import BorrowerModel


class Borrower:
    def extractBorrower(self, borrower):
        borrowerModel = BorrowerModel()
        borrowerModel.forename = borrower['forename']
        borrowerModel.middlename = borrower['middle_name']
        borrowerModel.surname = borrower['surname']
        borrowerModel.dob = borrower['dob']
        borrowerModel.gender = borrower['gender']
        borrowerModel.phonenumber = borrower['phone_number']
        borrowerModel.address = borrower['address']

        borrowerModel.save()

        return borrowerModel.id
