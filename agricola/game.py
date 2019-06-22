import itertools
import numpy as np
import copy
import json
import sys, os
import subprocess
import argparse
import datetime
import uuid

sys.path.append(os.getcwd())

#from agricola import TextInterface, AgricolaException
from .errors import AgricolaException
from .ui import TextInterface
from .player import Player
from .action import *
from .cards import (
  get_occupations, get_minor_improvements, get_major_improvements)
from .utils import EventGenerator, EventScope, dbgprint
from .step import ActionSelectionStep
from .choice import Choice
from . import const
# TODO: make sure that certain actions which allow two things to be done have
# the order of the two things respected (and make sure player can't take the
# action if they can't take the first action.


class Deck(object):
  """ A list of cards combined with a method for drawing them. """

  def __init__(self, cards, cards_per_player, shuffle=True):
    self.cards = list(cards)
    self.cards_per_player = cards_per_player
    self.shuffle = shuffle

  def draw_cards(self, n_players):
    if self.shuffle:
      cards = np.random.choice(
        self.cards, n_players * self.cards_per_player, replace=False)
      np.random.shuffle(cards)
      cards = list(cards)
    else:
      cards = self.cards + []

    hands = []
    for i in range(n_players):
      hand = cards[i*self.cards_per_player:(i+1)*self.cards_per_player]
      hands.append(hand)
    return hands

class AgricolaGame(EventGenerator):
  """ An object storing the stage for a game of Agricola.

  Parameters
  ----------
  actions: list of list of actions
    The actions to include in the game. The first sublist corresponds
    to actions that are available from the beginning of the game. Each
    subsequent list gives the actions that become available in the
    corresponding stage.
  n_players: int > 0
    Number of players.
  initial_players: Player instance or list thereof (optional)
    If a Player instance, each player is created as a copy of this player.
    If a list, length must be equal to ``n_players`` (allows specifying
    different starting configurations for different players). If not
    supplied, the default starting configuration is used for every player.
  occupations: instance of Deck
    Pool of occupations to draw from.
  minor_improvements: instance of Deck
    Pool of minor improvements to draw from.
  major_improvements: list of MajorImprovement instances
    Pool of major improvements to draw from.
  randomize: bool (default: True)
    If False, respect the within-stage ordering of actions in ``actions``.
    Otherwise, randomize the order of the actions within a stage.

  """
  def __init__(
      self, actions, n_players, game_id, initial_players=None,
      occupations=None, minor_improvements=None, major_improvements=None,
      randomize=True):

    self.game_id = game_id
    self.actions = actions
    self.n_players = n_players

    # 0 is always first player
    self.set_first_player(0)

    if isinstance(initial_players, list):
      if not len(initial_players) == n_players:
        raise ValueError(
          "Length of list ``initial_players`` must "
          "be equal to ``n_players``.")
      elif not all(isinstance(p, Player) for p in initial_players):
        raise ValueError(
          "``initial_players`` must be an agricola.Player instance or "
          "a list thereof.")
    elif initial_players is None:
      initial_players = [Player(str(i), food = 2 if i == 0 else 3 ) for i in range(self.n_players)]
    elif not isinstance(initial_players, Player):
      raise ValueError(
        "``initial_players`` must be an agricola.Player instance or "
        "a list thereof.")
    self.initial_players = initial_players

    try:
      occupations = list(occupations)
      occupations = Deck(occupations, 7)
    except:
      pass
    self.occupations = occupations

    try:
      minor_improvements = list(minor_improvements)
      minor_improvements = Deck(minor_improvements, 7)
    except:
      pass
    self.minor_improvements = minor_improvements

    self.major_improvements = major_improvements or []

    self.randomize = randomize

    super(AgricolaGame, self).__init__()

  def __str__(self):
    s = ["<AgricolaGame \n\n"]
    s.append("Actions taken:\n")
    for action, player in self.actions_taken.items():
      s.append("{0} -> Player {1}\n".format(action, player))
    s.append("\nActions remaining:\n")
    for action in self.actions_remaining:
      s.append("{0}\n".format(action))
    s += ">"
    return ''.join(s)

  def get_state_dict(self, current_event, event_source):
    round_action_array = []
    for stage_action in self.action_order[1:]:
      for round_action in stage_action:
        round_action_array.append(round_action.get_id())

    action_array = []
    for action_taken in self.actions_taken:
      action_dict = action_taken.get_state_dict()
      action_dict["is_available"] = False
      action_dict["taken_by"] = self.actions_taken[action_taken]
      action_array.append(action_dict)

    for action_available in self.actions_remaining:
      action_dict = action_available.get_state_dict()
      action_dict["is_available"] = True
      action_array.append(action_dict)

    remaining_major_improvements = list(map(lambda mi: mi.name, self.major_improvements))
    
    player_dicts = list(map(lambda p: p.get_state_dict(), self.players))

    state_dict = {
      "current_stage": self.stage_idx,
      "current_round": self.round_idx,
      "current_player": self.current_player_idx,
      "current_event": current_event,
      "event_source": event_source,
      "start_player": self.first_player_idx,
      "common_board": {
        "round_cards": round_action_array,
        "actions": action_array,
        "remaining_major_improvements": remaining_major_improvements
      },
      "players": player_dicts
    }

    return state_dict

  def _validate_event_name(self, event_name):
    return event_name in [
      'start_round',
      'start_stage',
      'end_round',
      'end_stage',
      'field_phase',
      'feeding_phase',
      'breeding_phase',
      'renovation',
      'build_room',
      'build_pasture',
      'build_stable'
      'plow_field',
      'birth',
      'occupation',
      'minor_improvement',
      'major_improvement'
    ] or event_name.startswith('Action: ')

  def set_first_player(self, idx):
    self.first_player_idx = idx

  @property
  def rounds_remaining(self):
    """ Complete rounds remaining (i.e. doesn't include current round). """
    return sum([len(s) for s in self.actions[1:]]) - self.round_idx

  def get_choices(self, player, _choices):
    return_as_list = True
    if isinstance(_choices, Choice):
      _choices = [_choices]
      return_as_list = False

    choices = self.ui.get_choices(player.name, _choices)

    if not return_as_list:
      choices = choices[0]

    return choices


def play(game, ui, agent_processes, logdir):
  game.ui = ui
  if game.randomize:
    game.action_order = (
      [game.actions[0]] +
      [np.random.permutation(l) for l in game.actions[1:]])
  else:
    game.action_order = game.actions

  game.players = [copy.deepcopy(ip) for ip in game.initial_players]
  for i, p in enumerate(game.players):
    p.index = i
    p.name = str(i)

  for p in game.players:
    p.set_game(game)

  if game.occupations:
    hands = game.occupations.draw_cards(game.n_players)
    for hand, player in zip(hands, game.players):
      player.give_cards('occupations', hand)

  if game.minor_improvements:
    hands = game.minor_improvements.draw_cards(game.n_players)
    for hand, player in zip(hands, game.players):
      player.give_cards('minor_improvements', hand)

  ui.start_game(game)

  game.round_idx = 1
  game.stage_idx = 1
  game.actions_taken = {}

  for p in game.players:
    print(p)

  # Main loop
  game.active_actions = [a for a in game.action_order[0]]
  for stage_actions in game.action_order[1:]:
    ui.begin_stage(game.stage_idx)
    for round_action in stage_actions:
      game.active_actions.append(round_action)
      for action in game.active_actions:
        action.turn()

      game.actions_remaining = game.active_actions + []

      ui.begin_round(game.round_idx, round_action)

      for p in game.players:
        p.turn_left = p.people
      remaining_players = set(range(len(game.players)))
      order = list(range(game.n_players))
      order = order[game.first_player_idx:] + order[:game.first_player_idx]
      game.actions_taken = {}

      for i in itertools.cycle(order):
        if i in remaining_players:
          action = None
          is_previous_action_failed = False

          popen = agent_processes[i]

          game_copy = copy.deepcopy(game)
          player = game_copy.players[i]
          game_copy.current_player_idx = i

          # initialize step stack
          step_stack = [ActionSelectionStep]

          try:

            while len(step_stack) > 0:
              dbgprint(step_stack)
              next_step = step_stack.pop()(game_copy, player)
              dbgprint(step_stack)
              dbgprint(next_step)
              next_choice_class, next_source_name = next_step.get_required_choice_and_source()
              choice = None
              
              if next_choice_class:
                # get player choice
                state_dict = game_copy.get_state_dict(
                  next_choice_class.__name__,
                  next_source_name)

                # send the context of current choice
                state_json = json.dumps(state_dict)

                # send state to agent
                popen.stdin.write(state_json + "\n")
                popen.stdin.flush()

                # get action from agent
                popen.stdout.flush()
                player_action = popen.stdout.readline()
                choice_dict = json.loads(player_action)
                dbgprint(next_choice_class)
                choice = next_choice_class(game_copy, player, choice_dict)

                state_dict["player_output"] = choice_dict
                log_state_json = json.dumps(state_dict)

                # write to log file
                state_log_path = logdir + "/" + game.game_id + "_state.json"
                with open(state_log_path, mode='a') as f:
                  f.write(log_state_json + "\n")

              additional_steps = next_step.effect(choice)
              if additional_steps:
                step_stack = additional_steps + step_stack
                dbgprint(step_stack)
                dbgprint(additional_steps)
            

            # state_dict = game.get_state_dict(
            #   'ActionChoice',
            #   const.event_sources.game,
            # )
            # state_dict["is_previous_action_failed"] = is_previous_action_failed
            # state_json = json.dumps(state_dict)
            # is_previous_action_failed = False

            # # send state to agent
            # popen.stdin.write(state_json + "\n")
            # popen.stdin.flush()

            # # get action from agent
            # popen.stdout.flush()
            # player_action = popen.stdout.readline()
            # json_action = json.loads(player_action)
            # state_dict["player_output"] = json_action
            # log_state_json = json.dumps(state_dict)

            # # write to log file
            # state_log_path = logdir + "/" + game.game_id + "_state.json"
            # with open(state_log_path, mode='a') as f:
            #   f.write(log_state_json + "\n")

            # # search class from actions_remaining and action taken
            # selected_action = list(filter(lambda x: x.__class__.__name__ == json_action["action_id"], game_copy.actions_remaining + list(game_copy.actions_taken.keys())))
            # action = selected_action[0] if len(selected_action) else None

            # if action is None:
            #   raise AgricolaException("No action chosen")
            # elif action not in game_copy.actions_remaining:
            #   raise AgricolaException("That action is not available this round")
            # elif action in game_copy.actions_taken:
            #   raise AgricolaException(
            #     "That action has already been taken by "
            #     "player {0}".format(game_copy.actions_taken[action]))

            # json_choices = []
            # choices = []

            # while True:
            #   choices, next_choice = action.choices(player, json_choices)
            #   if not next_choice:
            #     break

            #   # get next choice for player
            #   state_dict = game.get_state_dict(next_choice["class"].__name__,
            #                                    next_choice["source"])

            #   # send the context of current choice
            #   state_json = json.dumps(state_dict)

            #   # send state to agent
            #   popen.stdin.write(state_json + "\n")
            #   popen.stdin.flush()

            #   # get action from agent
            #   popen.stdout.flush()
            #   player_action = popen.stdout.readline()
            #   json_action = json.loads(player_action)
            #   json_choices.append(json_action)
            #   state_dict["player_output"] = json_action
            #   log_state_json = json.dumps(state_dict)

            #   # write to log file
            #   state_log_path = logdir + "/" + game.game_id + "_state.json"
            #   with open(state_log_path, mode='a') as f:
            #     f.write(log_state_json + "\n")

            # event_name = "Action: {}".format(action.__class__.__name__)
            # with EventScope([game_copy, player], event_name, 
            #                 player=player, action=action):
            #   print('choices:', choices)
            #   action.effect(player, choices)
            #   #exit(1)
            del game
            game = game_copy

          except AgricolaException as e:
            print(e)
            ui.action_failed(str(e))
            action = None
            is_previous_action_failed = True
            del game_copy

          ui.update_game(game)
          ui.action_successful()

          for p in game.players:
            print(p)

          if game.players[i].turn_left <= 0:
            remaining_players.remove(i)
            if not remaining_players:
              break

      ui.end_round()
      game.round_idx += 1

    ui.harvest()
    for p in game.players:
      p.harvest()
    ui.end_stage()

    game.stage_idx += 1

  game.score = {}
  for i, p in enumerate(game.players):
    game.score[i] = p.score()
  game.ui = None


class SimpleAgricolaGame(AgricolaGame):
  def __init__(self, n_players):
    from agricola.action import Lessons
    actions = get_simple_actions()
    occupations = Deck(get_occupations(n_players), 7)
    actions[0].append(Lessons())

    super(SimpleAgricolaGame, self).__init__(
      actions, n_players, occupations=occupations)


class LessonsAgricolaGame(AgricolaGame):
  def __init__(self, n_players):
    from agricola.action import Farmland, Fencing
    n_base = 4
    n_rounds = 2
    n_phases = 3
    actions = [[Fencing() for i in range(n_base)]]
    actions.extend([[Farmland() for i in range(n_rounds)] for j in range(n_phases)])
    occupations = get_occupations(n_players)

    super(LessonsAgricolaGame, self).__init__(
      actions, n_players, occupations=occupations)


class StandardAgricolaGame(AgricolaGame):
  def __init__(self, n_players, game_id, family=False):
    actions = get_actions(family, n_players)

    if family:
      occupations, minor_improvements = None, None
    else:
      occupations = get_occupations(n_players)
      minor_improvements = get_minor_improvements()

    major_improvements = get_major_improvements()

    super(StandardAgricolaGame, self).__init__(
      actions, n_players, game_id,
      occupations=occupations,
      minor_improvements=minor_improvements,
      major_improvements=major_improvements)

