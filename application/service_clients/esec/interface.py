class EsecClientInterface(object):  # pragma: no cover
    def __init__(self, implementation):
        self.implementation = implementation

    def initiate_signing(self, first_name, last_name, organisation_id, phone_number):
        return self.implementation.initiate_signing(first_name, last_name, organisation_id, phone_number)

    def reissue_auth_code(self, esec_user_name):
        return self.implementation.reissue_auth_code(esec_user_name)

    def verify_auth_code_and_sign(self, deed_xml, borrower_pos, user_id, borrower_auth_code):
        return self.implementation.verify_auth_code_and_sign(deed_xml, borrower_pos, user_id, borrower_auth_code)
