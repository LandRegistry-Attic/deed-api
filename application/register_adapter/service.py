from application.service_clients import register_adapter


class RegisterAdapter:

    @staticmethod
    def get_proprietor_names(title_number):
        register_adapter_client = register_adapter.make_register_adapter_client()
        borrower_names = register_adapter_client.get_proprietor_names(title_number)
        return borrower_names
