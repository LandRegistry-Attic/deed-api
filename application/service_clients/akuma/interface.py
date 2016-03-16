class AkumaInterface(object):  # pragma: no cover

    def __init__(self, implementation):
        self.implementation = implementation

    def perform_check(self, payload):
        return self.implementation.perform_check(payload)
