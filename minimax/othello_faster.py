#!/usr/bin/python2
import time
from math import exp,floor
from numpy import argmax


def pick_depth(x):
    return floor(7.85726*exp(-0.0710464*x))


def cross(A,B):
    return [a+b for a in A for b in B]


def units(s):
    sright = [s[0]+cols[i] for i in range(cols.find(s[1])+1,len(cols))]
    sup = [rows[i]+s[1] for i in range(rows.find(s[0]))][::-1]
    sleft = [s[0]+cols[i] for i in range(cols.find(s[1]))][::-1]
    sdown = [rows[i]+s[1] for i in range(rows.find(s[0])+1,len(rows))] 
    sup_right = [u[0]+r[1] for u,r in zip(sup,sright)]
    sup_left = [u[0]+l[1] for u,l in zip(sup,sleft)]
    sdown_left = [d[0]+l[1] for d,l in zip(sdown,sleft)]
    sdown_right = [d[0]+r[1] for d,r in zip(sdown,sright)]
    return [sright,sup_right,sup,sup_left,sleft,sdown_left,sdown,sdown_right]


def surrounding(s):
    return [u[0] for u in dirs[s] if u]


rows = 'ABCDEFGH'
cols = '12345678'
squares = cross(rows,cols)
dirs = dict((s, units(s)) for s in squares)
surs = dict((s, surrounding(s)) for s in squares)
human_num = 1
comp_num = -1
TOTAL_MOVES = 60
moves_left = TOTAL_MOVES
depth = 6


class Board:
    def __init__(self, board, turn):
        self.brd = board.copy()
        self.next_moves = {
            comp_num: self.moves(comp_num),
            human_num: self.moves(human_num)
        }
        self.turn = turn
        self.heur,self.terminal = self._heur()

    def moves(self, player):
        starts = [k for k,v in self.brd.items() if v == player]
        checked = dict((k, [0,0,0,0,0,0,0,0]) for k in squares)
        validmoves = []
        for start in starts:
            for i,di in enumerate(dirs[start]):
                for j,move in enumerate(di):
                    if checked[move][i]:
                        break
                    elif self.brd[move] == player:
                        checked[move][i] = 1
                        checked[move][(i+4) % 8] = 1
                        continue
                    elif self.brd[move] == -player:
                        continue
                    elif self.brd[move] == 0:
                        if j > 0 and self.brd[di[j-1]] != player:
                            checked[move] = [1,1,1,1,1,1,1,1]
                            validmoves.append(move)
                        break
        return validmoves

    def check4win(self):
        if self.next_moves[-1] or self.next_moves[1]:
            return 0
        board_vals = self.brd.values()
        hums = board_vals.count(human_num)
        comps = board_vals.count(comp_num)
        if hums > comps:
            return 1
        elif comps > hums:
            return -1
        else:
            return 3

    def _heur(self):
        winner = self.check4win()
        if winner:
            return (0,winner*float('inf'))[winner == 1 or winner == -1],True
        h = 0
        # Fix Heuristic IT SUCKS
        h += (len(self.next_moves[1]) - len(self.next_moves[-1]))*3
        for m in self.next_moves[1]: # Minus because it's bad
            h -= len([1 for d in surs[m] if not self.brd[d]])
        for m in self.next_moves[-1]:
            h += len([1 for d in surs[m] if not self.brd[d]])
        return h,False

    def neighbor_nodes(self, player):
        for move in self.next_moves[player]:
            yield self.playermove(player, move)

    def playermove(self, player, move):
        board = self.brd.copy()
        board[move] = player
        for di in dirs[move]:
            go = False
            flips = []
            for m in di:
                if board[m] == 0:
                    break
                elif board[m] == player:
                    go = True
                    break
                flips.append(m)
            if go:
                for i in flips:
                    board[i] = player
        return Board(board, -player)
            
    def print_board(self):
        board = self.brd.copy()
        for k in board:
            if board[k] == -1:
                board[k] = 2
        print ('   \033[4m')+' '.join(cols)+'\033[0m'
        for r in rows:
            print '%s|' % r,
            for c in cols:
                print (' ','B','W')[board[r+c]],
            print


def negamax(n, d, alpha, beta, player):
    if d == 0 or n.terminal:
        return player*n.heur
    for child in n.neighbor_nodes(player):
        alpha = max(alpha, -negamax(child, d-1, -beta, -alpha, -player))
        if alpha >= beta:
            return alpha
    return alpha


times = []


def computermove(brd):
    global times
    global moves_left
    global depth
    x = time.time()
    children = [i for i in brd.neighbor_nodes(comp_num)]
    if not children:
        print 'Computer cannot move'
        return board

    depth = pick_depth(len(children))
    
    print 'Possible moves: %d, Depth: %d' % (len(children),depth)
    weights = []
    alpha = -float('inf')
    for child in children:
        alpha = max(alpha, negamax(child, depth, -float('inf'), float('inf'), -comp_num))
        weights.append(alpha)

    print weights
    optimal_move = children[argmax(weights)]

    finished_time = time.time()-x
    times.append(finished_time)
    print 'Elapsed time is {0} seconds'.format(finished_time)
    print
    moves_left -= 1
    optimal_move.print_board()
    return optimal_move


def done(board, won):
    global times
    board_vals = board.values()
    print 'Human: %d' % board_vals.count(human_num)
    print 'Computer: %d' % board_vals.count(comp_num)
    if won == human_num:
        print 'Human won'
    elif won == comp_num:
        print 'Computer won'
    else:
        print 'Tie'
    
    print
    print 'The longest time for the AI to make a move was {0} seconds'.format(
        max(times))

def main():
    global moves_left
    board = dict((s, 0) for s in squares)
    board['D4'] = -1
    board['D5'] = 1
    board['E4'] = 1
    board['E5'] = -1

    board = Board(board, human_num)

    board.print_board()
    usermoves = board.next_moves[human_num]
    while True:
        print
        print 'Valid moves are: '+str(usermoves)
        usermove = raw_input('Enter row and col: ').upper()
        if not usermove in usermoves:
            print 'Invalid choice'
            continue
        moves_left -= 1
        board = board.playermove(human_num, usermove)
        print
        board.print_board()
        won = board.check4win()
        if won:
            return done(board.brd,won)
        print 'Computer is attempting to move...'
        board = computermove(board)
        won = board.check4win()
        if won:
            return done(board.brd, won)
        usermoves = board.next_moves[human_num]
        while not usermoves:
            print 'Human cannot move'
            board = computermove(board)
            won = board.check4win()
            if won:
                return done(board.brd, won)
            usermoves = board.next_moves[human_num]

        
if __name__ == '__main__':
    main()
