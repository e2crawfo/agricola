from future.builtins.misc import input
import re

from .action import (
  SpaceChoice)
  #VariableLengthListChoice, SpaceChoice, DictChoice)


class UserInterface(object):
  def update_game(self, game):
    self.game = game

  def start_game(self, game):
    self.update_game(game)
    #print("Starting game")

  def begin_stage(self, stage_idx):
    print("\n" + ("^" * 20))
    #print("Beginning stage {0}".format(stage_idx))

  def begin_round(self, round_idx, action):
    # print("\n" + ("=" * 20))
    # print("Beginning round {0}".format(round_idx))
    # print("New action is: {0}.".format(action))
    pass

  def get_action(self, name, actions_remaining):
    # action = np.random.choice(list(ar))
    action = self.get_user_choice(
      name, DiscreteChoice(actions_remaining, "Take an action."))
    # print("Player {0} chooses action {1}.".format(name, action))
    return action

  def get_choices(self, name, choices):
    return [self.get_user_choice(name, c) for c in choices]

  def harvest(self):
    # print("Harvesting.")
      pass

  def end_round(self):
      pass
   # print(self.game)
   # for p in self.game.players:
   #     print(p)
   # print("End of round.")

  def end_stage(self):
      pass
      # print("End of stage.")

  def action_failed(self, msg):
      # print("Action failed: {0}.".format(msg))
      pass

  def action_successful(self):
      # print("Action successful. Result: ")
      # print("\n" + ("*" * 20))
      # print(self.game)
      # print("*" * 20 + "\n")
      pass

  def finish_game(self):
    # print("Game finished.")
    pass

  def get_next_response(self):
    return input()

  def get_user_choice(self, name, choice_spec):
    if isinstance(choice_spec, DictChoice):
      pass
    elif isinstance(choice_spec, DiscreteChoice):
      idx = None
      while idx is None:
        # print("Player {} choice: ".format(name))
        # print(choice_spec.desc)
        for i, opt in enumerate(choice_spec.options):
          print("  {}: {}".format(i, opt))
        option_strings = [str(opt).lower() for opt in choice_spec.options]

        response = self.get_next_response()
        if not response:
          return None

        try:
          idx = int(response)
          if idx < 0 or idx >= len(choice_spec.options):
            raise ValueError()
        except (ValueError, TypeError):
          response_lower = response.lower()
          selected = [
            i for i, s in enumerate(option_strings) if response_lower in s]
          if not selected:
              pass
              # print("x. {} is not a valid response.".format(response))
          elif len(selected) > 1:
              pass
              # print("x. multiple values match response {}.".format(response))
          else:
              idx = selected[0]

      return choice_spec.options[idx]

    elif isinstance(choice_spec, CountChoice):
      while True:
        # print("Player {0}, enter an integer "
        #     "(min: 0, max: {1}): ".format(name, choice_spec.n))
        # print(choice_spec.desc)

        response = self.get_next_response()

        try:
          _response = int(response)
          if _response < 0:
            raise Exception()
          if choice_spec.n is not None and _response > choice_spec.n:
            raise Exception()
          break
        except:
          print("x. {0} is not a valid response.".format(response), file=sys.stderr)

      return _response

    elif isinstance(choice_spec, ListChoice):
      responses = []
      for sc in choice_spec.subchoices:
        response = self.get_user_choice(name, sc)
        responses.append(response)
      return responses

    elif isinstance(choice_spec, VariableLengthListChoice):
      length = self.get_user_choice(name, CountChoice(choice_spec.mx, desc=choice_spec.desc))
      responses = []
      for i in range(length):
        response = self.get_user_choice(name, choice_spec.subchoice)
        responses.append(response)
      return responses
    elif isinstance(choice_spec, SpaceChoice):
      while True:
        # print("Player {0}, enter a grid co-ordinate (y, x): ".format(name))
        # print(choice_spec.desc)
        response = self.get_next_response()

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
          print("x. {0} is not a valid response.".format(response), file=sys.stderr)

      return _response
    else:
      raise NotImplementedError()


class _TestUIFinished(BaseException):
  pass


class _TestUI(UserInterface):
  def __init__(self, user_actions):
    # `user_actions` is a list of objects that is processed in order.
    # If an object is not callable, then it is taken as the response to
    # next request for a choice by the agricola game. If it is callable,
    # then it is called with the game as input before the next choice is
    # provided. Such functions allow checking that the state of the game
    # meets certain specifications at various points in the game.
    self.user_actions = iter(user_actions)

  def get_next_response(self):
    try:
      nxt = next(self.user_actions)
      while callable(nxt):
        nxt(self.game)
        nxt = next(self.user_actions)
      return nxt
    except StopIteration:
      raise _TestUIFinished()


class TextInterface(UserInterface):
  pass
