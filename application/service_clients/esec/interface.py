class EsecClientInterface(object):  # pragma: no cover
    def __init__(self, implementation):
        self.implementation = implementation

    def issue_sms(self, forenames, last_name, organisation_name, phone_number):
        return self.implementation.issue_sms(forenames, last_name, organisation_name, phone_number)

    def reissue_sms(self, esec_user_name):
        return self.implementation.reissue_sms(esec_user_name)

    def auth_sms(self, deed, borrower_pos, user_id, borrower_auth_code, borrower_token):
        return self.implementation.auth_sms(deed, borrower_pos, user_id, borrower_auth_code, borrower_token)

    def sign_document_with_authority(self, deed_xml):
        return self.implementation.sign_document_with_authority(deed_xml)

    def check_service_health(self):
        return self.implementation.check_health()
