#!/usr/bin/python2
import time
from math import exp,floor
from numpy import argmax


def pick_depth(x):
    return 6 #floor(7.85726*exp(-0.0710464*x))+1


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


rows = 'ABCDEFGH'
cols = '12345678'
squares = cross(rows,cols)
dirs = dict((s, units(s)) for s in squares)
human_num = 1
comp_num = -1
TOTAL_MOVES = 60
moves_left = TOTAL_MOVES
depth = 6


class Board:
    def __init__(self, board):
        self.brd = board
        self.avail_moves = {
            1: moves(self.brd, 1),
            -1: moves(self.brd, -1)}
        self.heur,self.terminal = self._heur()

    def _heur(self):
        winner = check4win(self.brd)
        if winner:
            return (0,winner*float('inf'))[winner == 1 or winner == -1],True
        h = 0
        h += (len(self.avail_moves[1]) - len(self.avail_moves[-1]))*2
        for k,v in self.brd.items():
            if v:
                h += v*(10 if k[0] in 'AH' else 1)
                h += v*(10 if k[1] in '18' else 1)
        return h,False

    def neighbor_nodes(self, player):
        for move in self.avail_moves[player]:
            yield playermove(self.brd.copy(),player,move)


def moves(board,player):
    starts = [k for k,v in board.items() if v == player]
    checked = dict((k, [0,0,0,0,0,0,0,0]) for k in squares)
    validmoves = []
    for start in starts:
        for i,di in enumerate(dirs[start]):
            for j,move in enumerate(di):
                if checked[move][i]:
                    break
                elif board[move] == player:
                    checked[move][i] = 1
                    checked[move][(i+4) % 8] = 1
                    continue
                elif board[move] == -player:
                    continue
                elif board[move] == 0:
                    if j > 0 and board[di[j-1]] != player:
                        checked[move] = [1,1,1,1,1,1,1,1]
                        validmoves.append(move)
                    break
    return validmoves


def playermove(board,player,move):
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
    return Board(board)


def check4win(b):
    hmoves = moves(b,human_num)
    cmoves = moves(b,comp_num)
    if hmoves or cmoves:
        return 0
    hums = len([k for k,v in b.items() if v == human_num])
    comps = len([k for k,v in b.items() if v == comp_num])
    if hums > comps:
        return 1
    elif comps > hums:
        return -1
    else:
        return 3

# Final attempt before switching to reinforcement learning
# switch back to minimax cutoff (no alpha beta) and thread
def pvs(n, d, alpha, beta, player):
    if d == 0 or n.terminal:
        return player*n.heur
    elif not n.avail_moves[player] and player == comp_num:
        return 10000000
    b = beta
    count = 0
    if d == depth:
        poss_moves = []
    for child in n.neighbor_nodes(player):
        score = -pvs(child, d-1 , -b, -alpha, -player)
        if alpha < score < beta and count != 0:
            score = -pvs(child, d-1, -beta, -alpha, -player)
        alpha = max(alpha, score)
        if d == depth:
            poss_moves.append(score)
        if alpha >= beta:
            break
        b = alpha + 1
        count += 1
    if d == depth:
        return poss_moves
    return alpha


times = []


def computermove(board):
    global times
    global moves_left
    global depth
    x = time.time()
    brd = Board(board)
    children = [i for i in brd.neighbor_nodes(comp_num)]
    if not children:
        print 'Computer cannot move'
        return board

    depth = pick_depth(len(children))
    
    print 'Possible moves: %d, Depth: %d' % (len(children),depth)
    poss_moves = pvs(brd, depth, -float('inf'), float('inf'), comp_num)

    print poss_moves

    optimal_move = children[argmax(poss_moves)]

    finished_time = time.time()-x
    times.append(finished_time)
    print 'Elapsed time is {0} seconds'.format(finished_time)
    print
    moves_left -= 1
    print_board(optimal_move.brd)
    return optimal_move.brd


def print_board(brd):
    board = brd.copy()
    for k in board:
        if board[k] == -1:
            board[k] = 2
    print ('   \033[4m')+' '.join(cols)+'\033[0m'
    for r in rows:
        print '%s|' % r,
        for c in cols:
            print (' ','B','W')[board[r+c]],
        print


def done(board, won):
    global times
    print 'Human: ' + str(len([k for k,v in board.items()
                               if v == human_num]))
    print 'Computer: ' + str(len([k for k,v in board.items()
                               if v == comp_num]))
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

    print_board(board)
    usermoves = moves(board,human_num)
    while True:
        print
        print 'Valid moves are: '+str(usermoves)
        usermove = raw_input('Enter row and col: ').upper()
        if not usermove in usermoves:
            print 'Invalid choice'
            continue
        moves_left -= 1
        board = playermove(board, human_num, usermove).brd
        print
        print_board(board)
        won = check4win(board)
        if won:
            return done(board,won)
        print 'Computer is attempting to move...'
        board = computermove(board)
        won = check4win(board)
        if won:
            return done(board, won)
        usermoves = moves(board, human_num)
        while not usermoves:
            print 'Human cannot move'
            board = computermove(board)
            won = check4win(board)
            if won:
                return done(board, won)
            usermoves = moves(board, human_num)

        
if __name__ == '__main__':
    main()
