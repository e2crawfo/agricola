import json
import random

fence_taken = False
grain_planted = False

while True:
    try:
      state_string = input()
    except:
      break
    state_json = json.loads(state_string)
    player_json = state_json["players"][state_json["current_player"]]

    available_action = list(filter(lambda x: x["is_available"], state_json["common_board"]["actions"]))


    while True:
        if state_json["current_event"] == "SpaceChoice" and state_json["event_source"] == "plough":
            output_json = {
                "space": [4, 0]
            }
            break
        if state_json["current_event"] == "MinorImprovementchoice":
            output_json = {
                "minor_improvement_id": player_json["hand_improvements"][0]
            }
            break
        if state_json["current_event"] == "OccupationChoice":
            output_json = {
                "occupation_id": player_json["hand_occupations"][0]
            }
            break

        # choose action
        chosen_action = random.choice(available_action)
        if chosen_action["action_id"] == "FarmExpansion":
            pass
        elif chosen_action["action_id"] == "Farmland":
            continue
            if not "object_type" in player_json["board"][0][4]:
                output_json = {
                    "action_id": "Farmland"
                }
                break
        elif chosen_action["action_id"] == "Lessons":
            continue
            if len(player_json["hand_occupations"]) > 0:
                output_json = {
                    "action_id": "Lessons"
                }
                break
        elif chosen_action["action_id"] == "Lessons4P":
            pass
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
            continue
            if (not fence_taken) and player_json["resources"]["wood"] >= 8:
                output_json = {
                    "action_id": "Fencing",
                    "pastures": [[[4, 1], [4, 2], [3, 1], [3, 2]]]
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

