import curses
import numpy as np

from agricola.game import StandardAgricolaGame
from agricola.ui import UserInterface
from agricola.utils import draw_grid

FIELD = 1
MEADOW = 2
FENCE = 3
WOOD = 4
CLAY = 5
STONE = 6


class CursesInterface(UserInterface):
    def __init__(self, stdscr):
        self.stdscr = stdscr

        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(FIELD, curses.COLOR_BLACK, 137)
        curses.init_pair(MEADOW, curses.COLOR_BLACK, 34)
        curses.init_pair(FENCE, curses.COLOR_BLACK, 93)
        curses.init_pair(WOOD, curses.COLOR_BLACK, 52)
        curses.init_pair(CLAY, curses.COLOR_BLACK, 168)
        curses.init_pair(STONE, curses.COLOR_BLACK, 236)

    def _draw_player(self):
        player = self.game.players[0]
        player.plow_fields((0, 2))
        player.change_state('Add wood.', change={'wood': 15})
        player.build_pastures([[(2, 0), (2, 1)], [(2, 2), (1, 2)]])
        player.build_stables((0, 4), 1)
        grid = np.tile('.', player.shape)

        room_spaces = set(player.room_spaces)
        stable_spaces = set(player.stable_spaces)
        field_spaces = set(player.field_spaces)

        for i in range(player.shape[0]):
            for j in range(player.shape[1]):
                space = i, j
                if space in room_spaces:
                    grid[space] = 'H'
                elif space in stable_spaces:
                    grid[space] = '^'
                elif space in field_spaces:
                    grid[space] = '~'
        _grid = draw_grid(grid, (3, 5), player.fences, asarray=True)

        curses.echo()
        self.stdscr.refresh()
        self.stdscr.getstr(1, 1)

        win = curses.newwin(_grid.shape[0]+2, _grid.shape[1]+2, 0, 0)
        win.border()
        win.bkgd(ord(' '))

        for i, row in enumerate(_grid):
            for j, c in enumerate(row):
                if c in {'|', '-', '+'}:
                    win.addch(1+i, 1+j, ord(c), curses.color_pair(FENCE))
                elif c in {'^'}:
                    win.addch(1+i, 1+j, ord(c))
                elif c in {'H'}:
                    win.addch(1+i, 1+j, ord(c), curses.color_pair(WOOD))
                elif c in {'.', ' '} | set(str(i) for i in range(10)):
                    win.addch(1+i, 1+j, ord(c), curses.color_pair(MEADOW))
                elif c in {'~'}:
                    win.addch(1+i, 1+j, ord(c), curses.color_pair(FIELD))
                else:
                    win.addch(1+i, 1+j, ord(c))

        win.refresh()

        self.stdscr.getstr(1, 1)

    def start_game(self, game):
        self.game = game
        print("Starting game")
        self._draw_player()

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


def f(stdscr):
    game = StandardAgricolaGame(2)
    ui = CursesInterface(stdscr)

    game.play(ui)

if __name__ == "__main__":
    curses.wrapper(f)
