from . import implementation, interface


def make_register_adapter_client():
    return interface.RegisterAdapterInterface(implementation)
