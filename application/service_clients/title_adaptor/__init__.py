from . import implementation, interface


def make_title_adaptor_client():
    return interface.TitleAdaptorInterface(implementation)
