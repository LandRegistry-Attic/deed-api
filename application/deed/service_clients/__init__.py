from . import implementation, interface


def make_esec_client():
    return interface.EsecClientInterface(implementation)
