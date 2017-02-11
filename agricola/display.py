import curses

from agricola.game import StandardAgricolaGame
from agricola.ui import TextInterface

def f(stdscr):
    # stdscr.addch(ord('a'))
    # stdscr.addch(2, 2, ord('a'))
    # stdscr.refresh()

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    # game = StandardAgricolaGame(2)
    # ui = TextInterface()
    # game.play(ui)

    height = 5; width = 40
    s = stdscr.getstr(1, 1)

    for i in range(4):
        win = curses.newwin(height, width, i*height, 0)
        win.border()
        win.bkgd(ord('.'))
        win.refresh()

    curses.echo()            # Enable echoing of characters


    #stdscr.addch(10, 10, ord('a'), curses.A_STANDOUT)
    #stdscr.addch(10, 10, ord('a'), curses.color_pair(1))
    #stdscr.refresh()
    s = stdscr.getstr(1, 1)

    print(s)


def g(stdscr):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    height = 5; width = 40
    s = stdscr.getstr(1, 1)

    for i in range(4):
        win = curses.newwin(height, width, i*height, 0)
        win.border()
        win.bkgd(ord('.'))
        win.refresh()

    curses.echo()

    s = stdscr.getstr(1, 1)

    print(s)


curses.wrapper(g)
