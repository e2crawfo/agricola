# coding: utf-8
import time
import itertools
import numpy as np
import copy
import json
import sys, os
import subprocess
import argparse
import datetime
import uuid
from pprint import pprint
sys.path.append(os.getcwd())

#from agricola import TextInterface, AgricolaException
from .errors import AgricolaException
from .ui import TextInterface
from .player import Player
from .action import *
from .cards import (
  get_occupations, get_minor_improvements, get_major_improvements)
from .utils import EventGenerator, EventScope, dbgprint, flatten, dbgprint
from .step import ActionSelectionStep, ResourceTradingStep, RoundStartStep, RoundEndStep, StageEndStep
from .choice import Choice
from . import const
# TODO: make sure that certain actions which allow two things to be done have
# the order of the two things respected (and make sure player can't take the
# action if they can't take the first action.


RANDOM_SEED = 0
np.random.seed(seed=RANDOM_SEED)

def communicate_with_player(game, next_choice, previous_error, logdir, popen):
  # add context of the current choice to the state
  state_dict = game.get_state_dict()
  state_dict['current_event'] = next_choice.name
  state_dict['choice_candidates'] = next_choice.summarized_candidates
  state_dict["is_previous_action_failed"] = True if previous_error else False
  if previous_error:
    state_dict["previous_error"] = previous_error
  state_json = json.dumps(state_dict)
  
  # send the state to agent
  popen.stdin.write(state_json + "\n")
  popen.stdin.flush()
  
  # receive the choice from agent
  popen.stdout.flush()
  players_choice = json.loads(popen.stdout.readline())
  
  # add player's choice to the state
  state_dict["player_output"] = players_choice

  
  # log current state 
  state_log_path = logdir + "/" + game.game_id + "_state.json"
  with open(state_log_path, mode='a') as f:
    f.write(json.dumps(state_dict) + "\n")
  return players_choice


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
    self.step_stack = []

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

    self.current_player_idx = 0
    self.round_idx = 0
    self.stage_idx = 1
    self.actions_taken = {}
    self.is_start_of_round = True
    self.is_end_of_stage = False
    self.is_end_of_game = False
    # if self.randomize:
    #     self.action_order = (
    #         self.actions[0],
    #         flatten([np.random.permutation(l) for l in self.actions[1:]]))
    # else:
    #     self.action_order = [self.actions[0], flatten(self.actions)]
    if self.randomize:
        self.action_order = flatten([np.random.permutation(l) for l in self.actions[1:]])
    else:
        self.action_order = flatten(self.actions[1:])
    self.active_actions = self.actions[0]

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

  # def get_state_dict(self, current_event, event_source):
  def get_state_dict(self):
    round_action_array = []
    # for stage_action in self.action_order[1:]:
    #   for round_action in stage_action:
    #     round_action_array.append(round_action.get_id())
    for new_action in self.action_order:
        round_action_array.append(new_action.get_id())
    #   for round_action in stage_action:
    #     round_action_array.append(round_action.get_id())

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
      # "current_event": current_event,
      # "event_source": event_source,
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

  def add_steps(self, steps):
      if steps:
          assert type(steps) == list
          self.step_stack += list(reversed(steps))

  def pop_step(self):
      return self.step_stack.pop()

  def start_stage(self):
    self.ui.begin_stage(self.stage_idx)

  #def start_round(self, round_action):
  def start_round(self):
    self.round_idx += 1
    round_action = self.action_order[self.round_idx - 1]
    self.ui.begin_round(self.round_idx, round_action)
    self.actions_remaining = self.active_actions + []
    self.active_actions.append(round_action)
    for action in self.active_actions:
      action.turn()
    self.actions_taken = {}

    # Change the start player.
    new_order = list(range(self.n_players))
    new_order = new_order[self.first_player_idx:] + new_order[:self.first_player_idx]
    roundstart_stepstack = [RoundStartStep(self.players[i]) for i in new_order]
    self.add_steps(roundstart_stepstack)
    self.is_start_of_round = False
    return itertools.cycle(new_order)

  def start_turn(self, player_idx):
      player = self.players[player_idx]
      self.add_steps([ActionSelectionStep(player), ResourceTradingStep(player)])

  def end_round(self, player_order):
    self.ui.end_round()
    # for _ in range(self.n_players):
    #     i = player_order.__next__()
    #     self.players[i].end_round()

    if self.round_idx in [4, 7, 9, 11, 13, 14]:
        self.is_end_of_stage = True

    end_round_steps = []
    for _ in range(self.n_players):
        i = player_order.__next__()
        end_round_steps.append(RoundEndStep(self.players[i]))
    self.is_start_of_round = True
    self.add_steps(end_round_steps)

  def end_stage(self, player_order):
    self.ui.harvest()
    # for _ in range(self.n_players):
    #     i = player_order.next()
    #     self.players[i].harvest()

    self.ui.end_stage()
    self.stage_idx += 1

    end_stage_steps = []
    for _ in range(self.n_players):
        i = player_order.__next__()
        end_stage_steps.append(StageEndStep(self.players[i]))

    self.add_steps(end_stage_steps)
    self.is_end_of_stage = False

    if self.round_idx == 14:
        self.is_end_of_game = True

  @property
  def is_end_of_round(self):
    # ** player.turn_left can be less than 0 **
    return len([1 for j in range(self.n_players) if self.players[j].turn_left >= 1]) == 0 and len(self.step_stack) == 0 and not self.is_start_of_round


  def skip_turn(self, player_idx, e):
    print(e, file=sys.stderr)
    self.ui.action_failed(str(e))
    self.players[player_idx].turn_left -= 1
    self.step_stack = []
  
  def process_step(self, agent_processes, previous_error, logdir):
      next_step = self.pop_step()
      print('\tPlayer %d' % next_step.player.index, next_step.__class__.__name__)
      player_idx = next_step.player.index

      next_choice = next_step.get_required_choice(self)

      if next_choice and len(next_choice.candidates) != 1:
          players_choice = communicate_with_player(self, 
                                                   next_choice, 
                                                   previous_error,
                                                   logdir, 
                                                   agent_processes[player_idx])
          # read player's choice
          next_choice.read_players_choice(players_choice)
      additional_steps = next_step.effect(self, next_choice)
      self.add_steps(additional_steps)


def play(game, ui, agent_processes, logdir):
  game.ui = ui
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
  previous_error = ''

  while True:
      #print("<SOR>, <EOR>, <EOS>",game.is_start_of_round, game.is_end_of_round, game.is_end_of_stage, len(game.step_stack), file=sys.stderr)
      if game.is_end_of_stage and len(game.step_stack) == 0:
          print('<End Stage %d>' % game.stage_idx)
          game.end_stage(player_order)
      elif game.is_end_of_round:
          print('<End Round %d>' % game.round_idx)
          game.end_round(player_order)
      elif game.is_end_of_game and len(game.step_stack) == 0:
          print('<End of Game>')
          break
      elif game.is_start_of_round and not game.is_end_of_stage and len(game.step_stack) == 0:
          print('<Start Round %d: SP=%d>' % (game.round_idx + 1, game.first_player_idx))
          player_order = game.start_round()
      elif len(game.step_stack) == 0:
          player_idx = player_order.__next__()
          print("<Round %d: Player %d's turn (turns left=%d)>" % (game.round_idx, player_idx, game.players[player_idx].turn_left))
          game.current_player_idx = player_idx
          game.start_turn(player_idx)

      game_copy = copy.deepcopy(game)
      try:
          game_copy.process_step(agent_processes, previous_error, logdir)
          del game
          game = game_copy
          previous_error = ''
      except AgricolaException as e:
          game.skip_turn(player_idx, e)
          previous_error = str(e)
      ui.update_game(game)
      ui.action_successful()
      #time.sleep(1)

  exit(1)
  # ##################  Main loop  ########################
  # game.active_actions = [a for a in game.action_order[0]]
  # previous_error = ""
  # for stage_actions in game.action_order[1:]:
  #   game.start_stage()
  #   game.step_stack = []
  #   for round_action in stage_actions:
  #     player_order = game.start_round(round_action)

  #     for i in itertools.cycle(player_order):

  #       if game.is_end_of_round:
  #         break
  #       game.current_player_idx = i
  #       game.prevous_error = ''
  #       game_copy = copy.deepcopy(game)
  #       player = game_copy.players[i]

  #       # TODO: move optional trading step to proper position
  #       # TODO: do this ResourceTradingStap occur even if he have no family?
  #       game_copy.step_stack += [ActionSelectionStep(player), 
  #                                ResourceTradingStep(player)]
  #       try:
  #         while len(game_copy.step_stack) > 0:
  #           next_step = game_copy.step_stack.pop()
  #           next_choice = next_step.get_required_choice(game_copy)
  #           # print(game.stage_idx, game.round_idx, file=sys.stderr)
  #           # print(True if next_choice and len(next_choice.candidates) != 1 else False, file=sys.stderr)
  #           if next_choice and len(next_choice.candidates) != 1:
  #             players_choice = communicate_with_player(game_copy, 
  #                                                      next_choice, 
  #                                                      previous_error,
  #                                                      logdir, 
  #                                                      agent_processes[i])
  #             # read player's choice 
  #             next_choice.read_players_choice(players_choice)

  #           additional_steps = next_step.effect(game_copy, next_choice)
  #           if additional_steps:
  #             game_copy.step_stack += additional_steps
  #           previous_error = ''
  #         del game
  #         game = game_copy
  #       except AgricolaException as e:
  #         game.revert_failed_step(i, e)
  #         previous_error = str(e)
  #         del game_copy

  #       ui.update_game(game)
  #       ui.action_successful()
  #     game.end_round(player_order)
  #   game.end_stage(player_order)
  #   ##################  Main loop  ########################

  game.score = {}
  for i, p in enumerate(game.players):
    game.score[i] = p.score()
  game.ui = None
  state_log_path = game.logdir + "/" + game.game_id + "_state.json"
  sys.stderr.write('The game log was saved to \'%s\'.\n' % state_log_path)


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


