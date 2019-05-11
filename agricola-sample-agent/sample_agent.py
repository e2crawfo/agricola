import json
import random

fence_taken = False

while True:
    state_string = input()

    state_json = json.loads(state_string)
    player_json = state_json["players"][state_json["current_player"]]

    available_action = list(filter(lambda x: x["is_available"], state_json["common_board"]["actions"]))

    while True:
        chosen_action = random.choice(available_action)
        if chosen_action["action_id"] == "FarmExpansion":
            pass
        elif chosen_action["action_id"] == "Farmland":
            if len(player_json["board"][0][4]) == 0:
                output_json = {
                    "action_id": "Farmland",
                    "ploughing_space": [4, 0]
                }
                break
        elif chosen_action["action_id"] == "Lessons":
            pass
        elif chosen_action["action_id"] == "Lessons4P":
            pass
        elif chosen_action["action_id"] == "GrainUtilization":
            pass
        elif chosen_action["action_id"] == "Fencing":
            if (not fence_taken) and player_json["resources"]["wood"] >= 4:
                output_json = {
                    "action_id": "Fencing",
                    "pastures": [[[4, 1]]]
                }
                fence_taken = True
                break 
        elif chosen_action["action_id"] == "MajorImprovement":
            pass
        elif chosen_action["action_id"] == "HouseRedevelopment":
            pass
        elif chosen_action["action_id"] == "BasicWishForChildren":
            pass
        elif chosen_action["action_id"] == "Cultivation":
            pass
        elif chosen_action["action_id"] == "FarmRedevelopment":
            pass
        else:
            output_json = {
                "action_id": chosen_action["action_id"]
            }
            break
    print(json.dumps(output_json))

