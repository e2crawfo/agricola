import json
import random

while True:
    state_string = input()

    state_json = json.loads(state_string)

    available_action = list(filter(lambda x: x["is_available"], state_json["common_board"]["actions"]))

    while True:
        chosen_action = random.choice(available_action)
        if chosen_action["action_id"] == "FarmExpansion":
            pass
        elif chosen_action["action_id"] == "Farmland":
            pass
        elif chosen_action["action_id"] == "Lessons":
            pass
        elif chosen_action["action_id"] == "Lessons4P":
            pass
        elif chosen_action["action_id"] == "GrainUtilization":
            pass
        elif chosen_action["action_id"] == "Fencing":
            pass
        elif chosen_action["action_id"] == "MajorImprovement":
            pass
        elif chosen_action["action_id"] == "HouseRedevelopment":
            pass
        elif chosen_action["action_id"] == "BasicWishForChildren":
            pass
        elif chosen_action["action_id"] == "Cultivation":
            pass
        else:
            output_json = {
                "action_id": chosen_action["action_id"]
            }
            break
    print(json.dumps(output_json))

