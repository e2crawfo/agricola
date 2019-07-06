import json
import random

fence_taken = False
grain_planted = False
stable_count = 0

while True:
    try:
      state_string = input()
    except:
      break
    state_json = json.loads(state_string)
    player_json = state_json["players"][state_json["current_player"]]

    available_action = list(filter(lambda x: x["is_available"], state_json["common_board"]["actions"]))

    while True:
        if state_json["current_event"] == "PlowingChoice":
            output_json = {
                "space": [4, 0]
            }
            break
        if state_json["current_event"] == "HouseBuildingChoice":
            if player_json["resources"]["wood"] >= 5 and player_json["resources"]["reed"] >= 2:
                output_json = {
                    "space": [0, 2]
                }
                break
            else:
                output_json = {}
                break
        if state_json["current_event"] == "StableBuildingChoice":
            if player_json["resources"]["wood"] >= 2 and stable_count != 4:
                output_json = {
                    "space": [stable_count % 2 + 1, int(stable_count / 2)]
                }
                stable_count += 1
                break
            else:
                output_json = {}
                break
        if state_json["current_event"] == "FencingChoice":
            output_json = {
                "pastures": [[[4, 1], [4, 2], [3, 1], [3, 2]]]
            }
            break
        if state_json["current_event"] == "MinorImprovementChoice":
            output_json = {
                "minor_improvement_id": player_json["hand_improvements"][0]
            }
            break
        if state_json["current_event"] == "MajorImprovementChoice":
            if player_json["resources"]["clay"] >= 2:
                output_json = {
                    "improvement_id": state_json["common_board"]["remaining_major_improvements"][0]
                }
                break
            else:
                output_json = {}
                break
        if state_json["current_event"] == "OccupationChoice":
            output_json = {
                "occupation_id": player_json["hand_occupations"][0]
            }
            break

        # choose action
        chosen_action = random.choice(available_action)
        if chosen_action["action_id"] == "FarmExpansion":
            output_json = {
                "action_id": "FarmExpansion"
            }
            break
        elif chosen_action["action_id"] == "Farmland":
            if not "object_type" in player_json["board"][0][4]:
                output_json = {
                    "action_id": "Farmland"
                }
                break
        elif chosen_action["action_id"] == "Lessons":
            if len(player_json["hand_occupations"]) > 0:
                output_json = {
                    "action_id": "Lessons"
                }
                break
        elif chosen_action["action_id"] == "Lessons4P":
            if len(player_json["hand_occupations"]) > 0:
                output_json = {
                    "action_id": "Lessons4P"
                }
                break
        elif chosen_action["action_id"] == "GrainUtilization":
            continue
            if player_json["resources"]["grain"] >= 1 and "object_type" in player_json["board"][0][4] and not grain_planted:
                output_json = {
                    "action_id": "GrainUtilization",
                    "plant_grain_count": 1,
                    "plant_vegitable_count": 0,
                    "bake_grain_count": 0
                }
                grain_planted = True
                break
            elif player_json["resources"]["veg"] >= 1 and "object_type" in player_json["board"][0][4] and not grain_planted:
                output_json = {
                    "action_id": "GrainUtilization",
                    "plant_grain_count": 0,
                    "plant_vegitable_count": 1,
                    "bake_grain_count": 0
                }
                grain_planted = True
                break
        elif chosen_action["action_id"] == "Fencing":
            if (not fence_taken) and player_json["resources"]["wood"] >= 8:
                output_json = {
                    "action_id": "Fencing"
                }
                fence_taken = True
                break 
        elif chosen_action["action_id"] == "MajorImprovement":
            output_json = {
                "action_id": "MajorImprovement"
            }
            break 
        elif chosen_action["action_id"] == "HouseRedevelopment":
            output_json = {
                "action_id": "HouseRedevelopment"
            }
            break
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

