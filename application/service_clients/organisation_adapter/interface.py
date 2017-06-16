class OrganisationAdapterInterface(object):  # pragma: no cover
    def __init__(self, implementation):
        self.implementation = implementation

    def get_organisation_name(self, organisation_name):
        return self.implementation.get_organisation_name(organisation_name)

    def check_service_health(self):
        return self.implementation.check_health()
