from application.service_clients import title_adaptor
from copy import deepcopy


class TitleAdaptor:

    @staticmethod
    def do_check(title):

        title_adaptor_client = title_adaptor.make_title_adaptor_client()

        check_result = title_adaptor_client.perform_check(title)

        return check_result
