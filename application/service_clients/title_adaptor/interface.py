class TitleAdaptorInterface(object):  # pragma: no cover

    def __init__(self, implementation):
        self.implementation = implementation

    def perform_check(self, title):
        return self.implementation.perform_check(title)
