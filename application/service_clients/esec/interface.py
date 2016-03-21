class EsecClientInterface(object):  # pragma: no cover
    def __init__(self, implementation):
        self.implementation = implementation

    def issue_sms(self, first_name, last_name, organisation_id, phone_number):
        return self.implementation.issue_sms(first_name, last_name, organisation_id, phone_number)

    def reissue_sms(self, esec_user_name):
        return self.implementation.reissue_sms(esec_user_name)

    def auth_sms(self, deed_xml, borrower_pos, user_id, borrower_auth_code):
        return self.implementation.auth_sms(deed_xml, borrower_pos, user_id, borrower_auth_code)
