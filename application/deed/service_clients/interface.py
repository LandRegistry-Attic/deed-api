class EsecClientInterface(object):  # pragma: no cover
    def __init__(self, implementation):
        self.implementation = implementation

    def add_borrower_signature(self, deed_xml, borrower_pos):
        return self.implementation.add_borrower_signature(deed_xml, borrower_pos)