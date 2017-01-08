import numpy as np


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
        action = np.random.choice(list(ar))
        print("\n" + ("*" * 20))
        print(self.game)
        print("Player {0} chooses action {1}.".format(i, action))
        return action

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
        print("Action failed because: {0}.".format(msg))

    def action_successful(self):
        print("Action successful.")

    def finish_game(self):
        print("Game finished.")


class TextInterface(UserInterface):
    pass
