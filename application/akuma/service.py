from application.service_clients import akuma


class Akuma:

    @staticmethod
    def do_check(json_payload, check_type):
        payload = {
            "service": "digital mortgage",
            "activity": check_type,
            "payload": json_payload
        }

        akuma_client = akuma.make_akuma_client()

        check_result = akuma_client.perform_check(payload)

        return check_result
