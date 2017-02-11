from future.builtins.misc import input
import re

from agricola.action import (
    DiscreteChoice, CountChoice, ListChoice,
    VariableLengthListChoice, SpaceChoice)


def get_user_choice(player, choice_spec):
    if isinstance(choice_spec, DiscreteChoice):
        while True:
            print("Player {0} choice: ".format(player.name))
            print(choice_spec.desc)
            for i, opt in enumerate(choice_spec.options):
                print("    {0}: {1}".format(i, opt))

            response = input()
            if not response:
                return None

            try:
                idx = int(response)
                if idx < 0 or idx >= len(choice_spec.options):
                    raise ValueError()
            except (ValueError, TypeError):
                print("x. {0} is not a valid response.".format(response))
            else:
                _response = choice_spec.options[idx]
                break

        return _response

    elif isinstance(choice_spec, CountChoice):
        while True:
            print("Player {0}, enter an integer "
                  "(min: 0, max: {1}): ".format(player.name, choice_spec.n))
            print(choice_spec.desc)

            response = input()

            try:
                _response = int(response)
                if _response < 0:
                    raise Exception()
                if choice_spec.n is not None and _response > choice_spec.n:
                    raise Exception()
                break
            except:
                print("x. {0} is not a valid response.".format(response))

        return _response

    elif isinstance(choice_spec, ListChoice):
        responses = []
        for sc in choice_spec.subchoices:
            response = get_user_choice(player, sc)
            responses.append(response)
        return responses

    elif isinstance(choice_spec, VariableLengthListChoice):
        length = get_user_choice(player, CountChoice(desc="List length."))
        responses = []
        for i in range(length):
            response = get_user_choice(player, choice_spec.subchoice)
            responses.append(response)
        return responses
    elif isinstance(choice_spec, SpaceChoice):
        while True:
            print("Player {0}, enter a grid co-ordinate (y, x): ".format(player.name))
            print(choice_spec.desc)
            response = input()

            if not response:
                return None
            try:
                matches = re.finditer('\(([0-9]+) *, *([0-9]+)\)', response)
                if not matches:
                    raise Exception()
                matches = list(matches)
                if len(matches) > 1:
                    raise Exception()
                m = matches[0]
                _response = (int(m.group(1)), int(m.group(2)))
                break
            except:
                print("x. {0} is not a valid response.".format(response))

        return _response
    else:
        raise NotImplementedError()


class UserInterface(object):
    def start_game(self, game):
        self.game = game
        print("Starting game")

    def begin_stage(self, stage_idx):
        print("\n" + ("^" * 20))
        print("Beginning stage {0}".format(stage_idx))

    def begin_round(self, round_idx, action):
        print("\n" + ("=" * 20))
        print("Beginning round {0}".format(round_idx))
        print("New action is: {0}.".format(action))

    def get_action(self, i):
        ar = self.game.actions_remaining
        # action = np.random.choice(list(ar))
        action = get_user_choice(self.game.players[i], DiscreteChoice(ar, "Take an action."))
        print("\n" + ("*" * 20))
        print(self.game)
        print("Player {0} chooses action {1}.".format(i, action))
        return action

    def get_choices(self, player, choices):
        print(player)
        return [get_user_choice(player, c) for c in choices]

    def harvest(self):
        print("Harvesting.")

    def end_round(self):
        print(self.game)
        for p in self.game.players:
            print(p)
        print("End of round.")

    def end_stage(self):
        print("End of stage.")

    def action_failed(self, msg):
        print("Action failed: {0}.".format(msg))

    def action_successful(self):
        print("Action successful.")

    def finish_game(self):
        print("Game finished.")


class TextInterface(UserInterface):
    pass
