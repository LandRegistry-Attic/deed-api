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
        new_json = {
            "service": "Digital Mortgage",
            "activity": "Create",
            "payload": ""
                   }

        new_json["payload"] = json_payload

        check_result = Akuma.do_check(new_json)

        return check_result
