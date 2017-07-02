from future.utils import iteritems
import itertools
import copy
import numpy as np

from agricola import (
    Player, TextInterface, AgricolaException)
from agricola.action import get_actions, get_simple_actions
from agricola.cards import (
    get_occupations, get_minor_improvements, get_major_improvements)
from agricola.utils import EventGenerator, EventScope
from agricola.choice import Choice

# TODO: make sure that certain actions which allow two things to be done have
# the order of the two things respected (and make sure player can't take the
# action if they can't take the first action.


class Deck(object):
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
    """

    Parameters
    ----------
    actions: list of list of actions
        The actions to include in the game. The first sublist
        corresponds to actions that are available from the
        beginning of the game. Each subsequent list
        gives the actions that become available in the
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
        If False, respect the within-stage ordering of actions
        in ``actions``. Otherwise, randomize the order of the
        actions within a stage.

    """
    def __init__(
            self, actions, n_players, initial_players=None,
            occupations=None, minor_improvements=None, major_improvements=None,
            randomize=True):

        self.actions = actions
        self.n_players = n_players

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
            initial_players = [Player(str(i)) for i in range(self.n_players)]
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
        for action, player in iteritems(self.actions_taken):
            s.append("{0} -> Player {1}\n".format(action, player))
        s.append("\nActions remaining:\n")
        for action in self.actions_remaining:
            s.append("{0}\n".format(action))
        s += ">"
        return ''.join(s)

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

    def set_first_player(self, player):
        if isinstance(player, int):
            player = self.players[player]
        self.first_player = player

    @property
    def rounds_remaining(self):
        """ Complete rounds remaining (i.e. doesn't include current round). """
        return sum([len(s) for s in self.actions[1:]]) - self.round_idx

    def play(self, ui, first_player=None):
        self.ui = ui
        if self.randomize:
            self.action_order = (
                [self.actions[0]] +
                [np.random.permutation(l) for l in self.actions[1:]])
        else:
            self.action_order = self.actions

        self.players = [copy.deepcopy(ip) for ip in self.initial_players]
        for i, p in enumerate(self.players):
            p.name = str(i)

        for p in self.players:
            p.set_game(self)

        if self.occupations:
            hands = self.occupations.draw_cards(self.n_players)
            for hand, player in zip(hands, self.players):
                player.give_cards('occupations', hand)

        if self.minor_improvements:
            hands = self.minor_improvements.draw_cards(self.n_players)
            for hand, player in zip(hands, self.players):
                player.give_cards('minor_improvements', hand)

        if first_player is None:
            first_player = np.random.randint(self.n_players)
        self.set_first_player(first_player)

        players = self.players
        ui.start_game(self)

        self.round_idx = 1
        self.stage_idx = 1
        self.actions_taken = {}

        # Main loop
        self.active_actions = [a for a in self.action_order[0]]
        for stage_actions in self.action_order[1:]:
            ui.begin_stage(self.stage_idx)

            for round_action in stage_actions:
                self.active_actions.append(round_action)
                for action in self.active_actions:
                    action.turn()

                self.actions_remaining = self.active_actions + []

                ui.begin_round(self.round_idx, round_action)

                player_turns = [p.people for p in players]
                remaining_players = set(range(len(players)))

                order = list(range(self.n_players))
                first_player_idx = players.index(self.first_player)
                order = order[first_player_idx:] + order[:first_player_idx]
                self.actions_taken = {}

                for i in itertools.cycle(order):
                    if i in remaining_players:
                        player = self.players[i]
                        action = None
                        while action is None:
                            print("Player's status: ")
                            print(player)

                            action = ui.get_action(player.name, self.actions_remaining)

                            if action is None:
                                ui.action_failed("No action chosen")
                                continue
                            elif action not in self.actions_remaining:
                                ui.action_failed("That action is not available this round")
                                action = None
                                continue
                            elif action in self.actions_taken:
                                ui.action_failed(
                                    "That action has already been taken by "
                                    "player {0}".format(self.actions_taken[action]))
                                action = None
                                continue

                            choices = action.choices(player)
                            if choices:
                                choices = self.get_choices(player, choices)

                            event_name = "Action: {}".format(action.__class__.__name__)
                            try:
                                # TODO: We currently have no way to roll-back what
                                # goes on before an action occurs via pre-event triggers
                                # if the action fails
                                # which in some situations will give players access
                                # to pre-action effects without taking the action
                                # (if taking the action fails).
                                with EventScope([self, player], event_name, player=player, action=action):
                                    action.effect(player, choices)

                            except AgricolaException as e:
                                ui.action_failed(str(e))
                                action = None

                        ui.action_successful()

                        print("Player's status after action: ")
                        print(player)

                        self.actions_taken[action] = i
                        self.actions_remaining.remove(action)

                        player_turns[i] -= 1
                        if player_turns[i] <= 0:
                            remaining_players.remove(i)
                            if not remaining_players:
                                break

                ui.end_round()
                self.round_idx += 1

            ui.harvest()
            for p in players:
                p.harvest()
            ui.end_stage()

            self.stage_idx += 1

        self.score = {}
        for i, p in enumerate(players):
            self.score[i] = p.score()
        self.ui = None

    def get_choices(self, player, _choices):
        return_as_list = True
        if isinstance(_choices, Choice):
            _choices = [_choices]
            return_as_list = False

        choices = self.ui.get_choices(player.name, _choices)

        if not return_as_list:
            choices = choices[0]

        return choices


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
    def __init__(self, n_players, family=False):
        actions = get_actions(family, n_players)

        if family:
            occupations, minor_improvements = None, None
        else:
            occupations = get_occupations(n_players)
            minor_improvements = get_minor_improvements()

        major_improvements = get_major_improvements()

        super(StandardAgricolaGame, self).__init__(
            actions, n_players,
            occupations=occupations,
            minor_improvements=minor_improvements,
            major_improvements=major_improvements)


if __name__ == "__main__":
    # game = LessonsAgricolaGame(2)
    # game = SimpleAgricolaGame(2)
    game = StandardAgricolaGame(2)
    ui = TextInterface()
    game.play(ui)
