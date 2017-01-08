import abc
from future.utils import iteritems
import itertools
import copy

from agricola import Player, TextInterface, AgricolaInvalidChoice
from agricola.utils import check_random_state


# TODO: have classes for each of the configurations that are talked about in
# the agricola manual (e.g. 2 players, 3 player, 4 players, variations, etc.).

# TODO: to implement choices, each action can supply a list of choices to make,
# and can require that when taking the action, values for those choices are supplied.
# So a form of "lookahead".

# TODO: decide whether exceptions should be thrown or return True/False when actions can't be applied.


class Action(object):
    @abc.abstractmethod
    def __str__(self):
        raise NotImplemented()

    def choices(self, game):
        return []

    @abc.abstractmethod
    def condition(self, game, player, choices=None):
        return False

    @abc.abstractmethod
    def effect(self, game, player, choices=None):
        pass

    def turn(self):
        # Called at the beginning of every round.
        pass


class AlwaysApplies(Action):
    def condition(self, game, player, choices=None):
        return True


class ResourceAcquisition(AlwaysApplies):
    resources = {}

    def __str__(self):
        s = ["<" + self.__class__.__name__ + ":"]

        pairs = list(iteritems(self.resources))
        n_pairs = len(pairs)

        for i, (k, v) in enumerate(pairs[:-1]):
            s.append("+{0} {1},".format(v, k[2:]))
        if n_pairs > 1:
            s.append("and")
        s.append("+{0} {1}".format(pairs[-1][1], pairs[-1][0]))

        return ' '.join(s) + '>'

    def effect(self, game, player, choices=None):
        for resource, amount in iteritems(self.resources):
            setattr(player, resource, getattr(player, resource) + amount)


class Accumulating(ResourceAcquisition):
    acc_amount = {}

    def __init__(self):
        self.resources = {}
        for k, v in iteritems(self.acc_amount):
            self.resources[k] = 0

    def __str__(self):
        s = ["<" + self.__class__.__name__ + ":"]

        pairs = list(iteritems(self.resources))
        n_pairs = len(pairs)

        for i, (k, v) in enumerate(pairs[:-1]):
            s.append("+{0} {1},".format(v, k[2:]))
        if n_pairs > 1:
            s.append("and")
        s.append("+{0} {1}".format(pairs[-1][1], pairs[-1][0]))

        pairs = list(iteritems(self.acc_amount))
        n_pairs = len(pairs)

        s.append("(replenishes")
        for i, (k, v) in enumerate(pairs[:-1]):
            s.append("+{0} {1},".format(v, k[2:]))
        if n_pairs > 1:
            s.append("and")
        s.append("+{0} {1})".format(pairs[-1][1], pairs[-1][0]))

        return ' '.join(s) + '>'

    def effect(self, game, player, choices=None):
        super(Accumulating, self).effect(player)
        for resource in self.acc_amount:
            self.resources[resource] = 0

    def turn(self):
        for resource, amount in iteritems(self.acc_amount):
            self.resources[resource] += amount


class BasicWishForChildren(Action):
    def condition(self, game, player, choices=None):
        return player.people_avail > 0

    def effect(self, game, player, choices=None):
        player.add_people(1)


class ModestWishForChildren(Action):
    def condition(self, game, player):
        pass


class UrgentWishForChildren(Action):
    pass


class DayLaborer(ResourceAcquisition):
    resources = dict(food=2)


class Fishing(Accumulating):
    acc_amount = dict(food=1)


class TravellingPlayers(Fishing):
    pass


class Copse(Accumulating):
    acc_amount = dict(wood=1)


class Grove(Accumulating):
    acc_amount = dict(wood=2)


class Forest(Accumulating):
    acc_amount = dict(wood=3)


class ClayPit(Accumulating):
    acc_amount = dict(clay=1)


class Hollow(Accumulating):
    acc_amount = dict(clay=2)


class EasternQuarry(Accumulating):
    acc_amount = dict(stone=1)


class WesternQuarry(EasternQuarry):
    pass


class ResourceMarket2Player(ResourceAcquisition):
    resources = dict(food=1, stone=1)


class ResourceMarket3Player(ResourceAcquisition):
    resources = dict(food=1)

    def choices(self, game):
        return [("1 reed/1 stone", ["reed", "stone"])]

    def effect(self, game, player, choices=None):
        reed = choices[0] == 'reed'
        stone = choices[0] == 'stone'

        if not reed and not stone:
            raise AgricolaInvalidChoice()

        resources = self.resources.copy()
        resources[choices[0]] = 1

        for resource, amount in iteritems(self.resources):
            setattr(player, resource, getattr(player, resource) + amount)


class ResourceMarket4Player(ResourceAcquisition):
    resources = dict(food=1, stone=1, reed=1)


class ReedBank(Accumulating):
    acc_amount = dict(reed=1)


class SheepMarket(Accumulating):
    acc_amount = dict(sheep=1)


class PigMarket(Accumulating):
    acc_amount = dict(boar=1)


class CattleMarket(Accumulating):
    acc_amount = dict(cattle=1)


class AnimalMarket(ResourceAcquisition):
    resources = dict()

    def choices(self, game):
        return [("1 sheep, 1 food/1 boar/1 cow, -1 food", ["sheep", "boar", "cow"])]

    def effect(self, game, player, choices=None):
        resources = self.resources.copy()
        if choices[0] == "sheep":
            resources['food'] = 1
        elif choices[0] == "boar":
            pass
        elif choices[0] == "cow":
            resources['food'] = -1
        else:
            raise AgricolaInvalidChoice()

        resources[choices[0]] = 1

        for resource, amount in iteritems(self.resources):
            setattr(player, resource, getattr(player, resource) + amount)


class FarmExpansion(Action):
    def condition(self, game, player, choices=None):
        return len(player.empty_spaces) > 0

    def choices(self, game):
        return [("Locations.", None), ('Stable locations.', None)]

    def effect(self, game, player, choices=None):
        if len(choices) < 2:
            raise AgricolaInvalidChoice()

        if not isinstance(choices[0], list) and not isinstance(choices[1], list):
            raise AgricolaInvalidChoice("At least one of the two actions (build rooms or build stables) must be selected to use this action space.")

        room_spaces = choices[0]
        if room_spaces is None:
            pass
        elif isinstance(room_spaces, list):
            player.build_rooms(room_spaces)
        else:
            raise AgricolaInvalidChoice()

        stable_spaces = choices[0]
        if stable_spaces is None:
            pass
        elif isinstance(stable_spaces, list):
            player.build_stables(stable_spaces)
        else:
            raise AgricolaInvalidChoice()


class HouseRedevelopment(Action):
    pass


class FarmRedevelopment(Action):
    pass


class MajorImprovement(Action):
    pass


class Fencing(Action):
    pass


class Lessons(Action):
    pass


class Lessons3Player(Action):
    pass


class Lessons4Player(Action):
    pass


class MeetingPlace(Action):
    # TODO: consider passing in the overall game state along with the player state.
    def effect(self, game, player, choices=None):
        game.set_first(player)


class MeetingPlaceFamily(Accumulating, MeetingPlace):
    acc_amount = dict(food=1)

    def effect(self, game, player, choices=None):
        MeetingPlace.effect(self, game, player)
        Accumulating.effect(self, game, player)


class Farmland(Action):
    def condition(self, game, player, choices=None):
        return len(player.empty_spaces) > 0

    def effect(self, game, player, choices=None):
        # TODO: need to accept fields...
        player.plow_fields()


class Cultivation(Action):
    def condition(self, game, player, choices=None):
        return len(player.empty_spaces) > 0

    def effect(self, game, player, choices=None):
        # TODO: need to accept fields...
        player.plow_fields()


class GrainUtilization(Action):
    pass


class GrainSeeds(ResourceAcquisition):
    resources = dict(grain=1)


class VegetableSeeds(ResourceAcquisition):
    resources = dict(veg=1)


class SideJob(Action):
    pass


class CompoundAction(Action):
    pass


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
    randomize: bool (default: True)
        If False, respect the within-stage ordering of actions
        in ``actions``. Otherwise, randomize the order of the
        actions within a stage.

    """
    def __init__(self, actions, n_players, initial_player=None, randomize=True):
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
            initial_player = Player()
        elif not isinstance(initial_player, Player):
            raise ValueError(
                "``initial_player`` must be an agricola.Player instance or "
                "a list thereof.")
        self.initial_player = initial_player

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

        self.players = [copy.deepcopy(self.initial_player) for i in range(self.n_players)]
        self.first_player = first_player or rng.randint(self.n_players)

        players = self.players
        ui.start_game(self)

        round_idx = 1
        stage_idx = 1
        self.actions_taken = {}

        actions_avail = self.actions_avail = [a for a in self.action_order[0]]
        for stage_actions in self.action_order[1:]:
            ui.begin_stage(stage_idx)
            for round_action in stage_actions:
                actions_avail.append(round_action)
                for action in actions_avail:
                    action.turn()

                ui.begin_round(round_idx, round_action)

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
                            if action not in actions_avail:
                                ui.action_failed(
                                    "that action is not available this round")
                                action = None
                            elif action in self.actions_taken:
                                ui.action_failed(
                                    "that action has already been taken by "
                                    "player {0}".format(self.actions_taken[action]))
                                action = None

                            elif not action.condition(self, players[i]):
                                ui.action_failed(
                                    "player {0} does not meet the requirements "
                                    "for performing that action".format(i))

                                action = None
                        ui.action_successful()

                        action.effect(players[i])
                        self.actions_taken[action] = i

                        player_turns[i] -= 1
                        if player_turns[i] <= 0:
                            remaining_players.remove(i)
                            if not remaining_players:
                                break

                ui.end_round()
                round_idx += 1

            ui.harvest()
            for p in players:
                p.harvest()
            ui.end_stage()

            stage_idx += 1

        self.score = {}

        # Calculate score.
        for i, p in enumerate(players):
            self.score[i] = p.score()


if __name__ == "__main__":
    actions = [[Copse(), Grove(), Fishing()], [Forest(), DayLaborer()]]
    game = AgricolaGame(actions, 1)
    ui = TextInterface()
    game.play(ui)
