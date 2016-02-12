from application.borrower.model import Borrower


class BorrowerService:
    def saveBorrower(self, borrower, deed_token):
        borrowerModel = Borrower()
        borrowerModel.forename = borrower['forename']

        if 'middle_name' in borrower:
            borrowerModel.middlename = borrower['middle_name']

        borrowerModel.surname = borrower['surname']
        borrowerModel.dob = borrower['dob']
        borrowerModel.deed_token = deed_token

        if 'gender' in borrower:
            borrowerModel.gender = borrower['gender']

        borrowerModel.phonenumber = borrower['phone_number']
        borrowerModel.address = borrower['address']

        borrowerModel.token = borrowerModel.generate_token()

        borrowerModel.save()

        return borrowerModel
