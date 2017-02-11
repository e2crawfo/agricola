from future.utils import iteritems
import itertools
import copy

from agricola import (
    Player, TextInterface, AgricolaException)
from agricola.action import get_actions, get_simple_actions
from agricola.cards import get_occupations, get_minor_improvements, get_major_improvements
from agricola.utils import check_random_state

# TODO: make sure that certain actions which allow two things to be done have
# the order of the two things respected (and make sure player can't take the
# action if they can't take the first action.


class DefaultCardDrawer(object):
    def __init__(self, cards_per_player=7):
        self.cards_per_player = cards_per_player

    def draw_cards(self, n_players, deck, rng=None):
        rng = check_random_state(rng)

        cards = rng.choice(deck, n_players * self.cards_per_player, replace=False)
        rng.shuffle(cards)
        cards = list(cards)

        hands = []
        for i in range(n_players):
            hand = cards[i*self.cards_per_player:(i+1)*self.cards_per_player]
            hands.append(hand)
        return hands


class AgricolaGame(object):
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
    initial_player: list of Player instance or Player instance (optional)
        If a Player instance, each player is created as a copy of this player.
        If a list, length must be equal to ``n_players`` (allows specifying
        different starting configurations for different players). If not
        supplied, the default starting configuration is used for every player.
    occupations: list of Occupation instances
        Pool of occupations to draw from.
    minor_improvements: list of MinorImprovement instances
        Pool of minor improvements to draw from.
    major_improvements: list of MajorImprovement instances
        Pool of major improvements to draw from.
    randomize: bool (default: True)
        If False, respect the within-stage ordering of actions
        in ``actions``. Otherwise, randomize the order of the
        actions within a stage.

    """
    def __init__(
            self, actions, n_players, initial_player=None,
            occupations=None, minor_improvements=None, major_improvements=None,
            occ_card_drawer=None, mi_card_drawer=None, randomize=True):

        self.actions = actions
        self.n_players = n_players

        if isinstance(initial_player, list):
            if not len(initial_player) == n_players:
                raise ValueError(
                    "Length of list ``initial_player`` must "
                    "be equal to ``n_players``.")
            elif not all(isinstance(p, Player) for p in initial_player):
                raise ValueError(
                    "``initial_player`` must be an agricola.Player instance or "
                    "a list thereof.")
        elif initial_player is None:
            initial_player = Player("0")
        elif not isinstance(initial_player, Player):
            raise ValueError(
                "``initial_player`` must be an agricola.Player instance or "
                "a list thereof.")
        self.initial_player = initial_player

        self.occupations = occupations
        self.minor_improvements = minor_improvements
        self.major_improvements = major_improvements or []

        self.occ_card_drawer = occ_card_drawer or DefaultCardDrawer()
        self.mi_card_drawer = mi_card_drawer or DefaultCardDrawer()

        self.randomize = randomize

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

    def set_first_player(self, player):
        if isinstance(player, int):
            player = self.players[player]
        self.first_player = player

    @property
    def actions_remaining(self):
        return set(self.actions_avail) - set(self.actions_taken)

    def play(self, ui, first_player=None, rng=None):
        rng = check_random_state(rng)
        if self.randomize:
            self.action_order = (
                [self.actions[0]] +
                [rng.permutation(l) for l in self.actions[1:]])
        else:
            self.action_order = self.actions

        self.players = [
            copy.deepcopy(self.initial_player) for i in range(self.n_players)]
        for i, p in enumerate(self.players):
            p.name = str(i)

        if self.occupations:
            occ_hands = self.occ_card_drawer.draw_cards(
                self.n_players, self.occupations, rng)
            for hand, player in zip(occ_hands, self.players):
                player.give_cards('occupations', hand)

        if self.minor_improvements:
            mi_hands = self.mi_card_drawer.draw_cards(
                self.n_players, self.minor_improvements, rng)
            for hand, player in zip(mi_hands, self.players):
                player.give_cards('minor_improvements', hand)

        self.set_first_player(first_player or rng.randint(self.n_players))

        players = self.players
        ui.start_game(self)

        self.round_idx = 1
        self.stage_idx = 1
        self.actions_taken = {}

        # Main loop

        actions_avail = self.actions_avail = [a for a in self.action_order[0]]
        for stage_actions in self.action_order[1:]:
            ui.begin_stage(self.stage_idx)
            for round_action in stage_actions:
                actions_avail.append(round_action)
                for action in actions_avail:
                    action.turn()

                ui.begin_round(self.round_idx, round_action)

                player_turns = [p.people for p in players]
                remaining_players = set(range(len(players)))

                order = list(range(self.n_players))
                first_player_idx = players.index(self.first_player)
                order = order[first_player_idx:] + order[:first_player_idx]
                self.actions_taken = {}

                for i in itertools.cycle(order):
                    if i in remaining_players:
                        action = None
                        while action is None:
                            action = ui.get_action(i)

                            if action is None:
                                ui.action_failed("No action chosen")
                                continue
                            elif action not in actions_avail:
                                ui.action_failed("That action is not available this round")
                                action = None
                                continue
                            elif action in self.actions_taken:
                                ui.action_failed(
                                    "That action has already been taken by "
                                    "player {0}".format(self.actions_taken[action]))
                                action = None
                                continue

                            choices = action.choices(self, players[i])
                            if choices:
                                choices = ui.get_choices(self.players[i], choices)

                            try:
                                action.effect(self, players[i], choices)
                            except AgricolaException as e:
                                ui.action_failed(str(e))
                                action = None

                        ui.action_successful()

                        print("Player after action: ")
                        print(players[i])

                        self.actions_taken[action] = i

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

        # Calculate score.
        for i, p in enumerate(players):
            self.score[i] = p.score()


class SimpleAgricolaGame(AgricolaGame):
    def __init__(self, n_players):
        from agricola.action import Lessons
        actions = get_simple_actions()
        occupations = get_occupations(n_players)
        actions[0].append(Lessons())

        super(SimpleAgricolaGame, self).__init__(
            actions, n_players, occupations=occupations)


class LessonsAgricolaGame(AgricolaGame):
    def __init__(self, n_players):
        from agricola.action import Lessons, Farmland, Fencing
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
    #game = LessonsAgricolaGame(2)
    #game = SimpleAgricolaGame(2)
    game = StandardAgricolaGame(2)
    ui = TextInterface()
    game.play(ui)
