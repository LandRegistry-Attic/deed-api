from . import implementation, interface


def make_organisation_adapter_client():
    return interface.OrganisationAdapterInterface(implementation)
