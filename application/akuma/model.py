from application.config import AKUMA_URI
import requests
import json


class Akuma:

    @staticmethod
    def do_check(json_payload):

        url = AKUMA_URI
        payload = json_payload
        headers = {'content-type': 'application/json'}

        print (url)
        print ("Payload is " + str(payload))

        check_result = requests.post(url, data=json.dumps(payload), headers=headers)

        print (check_result.status_code)
        print (check_result.reason)
        print (check_result.raw)

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

        print ("Attempted to check " + str(new_json))

        check_result = Akuma.do_check(new_json)

        return check_result
