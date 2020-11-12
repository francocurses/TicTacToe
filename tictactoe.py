from curses import *
import _curses
import numpy as np

def main(stdscr):
    # get stdscr constants
    (LINES, COLS) = stdscr.getmaxyx()

    # needed to refresh windows
    stdscr.refresh()

    # curses configuration
    curs_set(False)
    echo()

    # border window
    borders = newwin(6,6,0,0)
    borders.box()
    borders.addstr(1,2,"abc")
    for i in range(1,4):
        borders.addstr(1+i,1,str(i))
    borders.refresh()

    # board window
    boardwin = borders.derwin(3,3,2,2)
    by, bx = boardwin.getmaxyx()
    for i in range(by):
        for j in range(bx):
            if (i+j)%2:
                boardwin.chgat(i,j,1,A_REVERSE)

    boardwin.refresh()
    
    # input and ouput prompt
    stdscr.addstr(7,0,"Type command:")
    iy = 7; ix = 14
    iprompt  = newwin(1,3,iy,ix)
    oprompt = newwin(2,COLS,8,0)
    
    # redraw before loop
    stdscr.refresh()

    turn = 0
    while True:
        # update player turn
        p = players[turn%2]
        oprompt.addstr(0,0,"Player "+p+" turn")
        oprompt.refresh()

        # get input
        iprompt.move(0,0)
        ipt = iprompt.getstr().decode()
        iprompt.clear()
        move = getmove(ipt)

        # handle invalid input
        if move is None:
            oprompt.addstr(1,0," "*(COLS-1))
            oprompt.addstr(1,0,"Invalid command")
            oprompt.refresh()
            continue

        y = move[0]
        x = move[1]
        
        # handle used space
        if board[y,x]!=0:
            oprompt.addstr(1,0," "*(COLS-1))
            oprompt.addstr(1,0,"Cell is used")
            continue

        # handle valid input
        board[y,x] = (turn%2)*2 - 1
        a = boardwin.inch(y,x)
        try:
            boardwin.addstr(y,x,p,a)
        except _curses.error as e:
            pass
        boardwin.refresh()

        # check victory
        win = check_victory(y,x)
        if win:
            winstr = "Player "+p+" wins!"
            oprompt.clear()
            oprompt.addstr(0,0,winstr)
            oprompt.refresh()
            finish(stdscr)

        # check end of game
        if np.all(board):
            oprompt.clear()
            oprompt.addstr(0,0,"Tie!")
            oprompt.refresh()
            finish(stdscr)

        # finish turn
        oprompt.clear()
        turn +=1
        
# game parameters
players = ["O", "X"]
board = np.zeros((3,3),dtype=int)

def getmove(cmd):
    """
    Translate a string command into a game move.
    Return None if invalid command.
    """
    cols = ["a","b","c"]
    rows = ["1","2","3"]

    if len(cmd) != 2:
        return None

    x = cmd[0]
    y = cmd[1]

    if x not in cols or y not in rows:
        return None
    
    x = ord(x) - 97
    y = int(y) - 1

    return (y,x)

def check_victory(y,x):
    """
    Check for victory in the board, given last
    move (y,x).
    """
    # get check lines
    cols = board.shape[1]
    diag1 = np.diag(board,x-y)
    diag2 = np.diag(np.fliplr(board),cols-1-x-y)
    horiz = board[y,:]
    verti = board[:,x]
    lines = [diag1,diag2,horiz,verti]

    # chech
    for line in lines:
        if abs(sum(line))>=3:
            return True

    return False

def finish(stdscr):
    """
    Finish the game.
    """
    noecho()
    while True:
        stdscr.getkey()

wrapper(main)
