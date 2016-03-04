class EsecClientInterface(object):  # pragma: no cover
    def __init__(self, implementation):
        self.implementation = implementation

    def sign_by_user(self, deed_xml, borrower_pos, user_id):
        return self.implementation.sign_by_user(deed_xml, borrower_pos, user_id)

    def initiate_signing(self, first_name, last_name, organisation_id):
        return self.implementation.initiate_signing(first_name, last_name, organisation_id)
