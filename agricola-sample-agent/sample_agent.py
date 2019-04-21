import json

while True:
    state_string = input()

    state_json = json.loads(state_string)

    output_json = {
        "action_id": state_json["common_board"]["actions"][0]["action_id"]
    }
    print(json.dumps(output_json))

