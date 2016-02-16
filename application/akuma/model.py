from application.config import AKUMA_URI
import requests
import json


class Akuma:

    @staticmethod
    def do_check(json_payload):

        url = AKUMA_URI
        payload = json_payload
        headers = {'content-type': 'application/json'}

        check_result = requests.post(url, data=json.dumps(payload), headers=headers)

        return json.loads(check_result.text)

    @staticmethod
    def creation_check(json_payload):

        # Wrap with Create activities
        create_json = {
            "service": "Digital Mortgage",
            "activity": "Create",
            "payload": ""
                   }

        create_json["payload"] = json_payload

        check_result = Akuma.do_check(create_json)

        return check_result

    @staticmethod
    def viewing_check(json_payload):

        # Wrap with Create activities
        view_json = {
            "service": "Digital Mortgage",
            "activity": "View",
            "payload": ""
                   }

        view_json["payload"] = json_payload

        check_result = Akuma.do_check(view_json)

        return check_result
