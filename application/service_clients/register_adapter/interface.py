

class RegisterAdapterInterface(object):  # pragma: no cover
    def __init__(self, implementation):
        self.implementation = implementation

    def get_proprietor_names(self, title_number):
        return self.implementation.get_proprietor_names(title_number)
