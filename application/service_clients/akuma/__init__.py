from . import implementation, interface


def make_akuma_client():
    return interface.AkumaInterface(implementation)
