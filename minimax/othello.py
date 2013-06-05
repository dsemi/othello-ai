#!/usr/bin/python2
import numpy, time
from math import fabs
from random import randint
import cPickle as pickle

steps = [[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]]
human_num = 1
comp_num = -1
generate = 0
board_h = [
    [1.00, -.25, 0.10, 0.05, 0.05, 0.10, -.25, 1.00],
    [-.25, -.25, 0.01, 0.01, 0.01, 0.01, -.25, -.25],
    [0.10, 0.01, 0.05, 0.02, 0.02, 0.05, 0.01, 0.10],
    [0.05, 0.01, 0.02, 0.01, 0.01, 0.02, 0.01, 0.05],
    [0.05, 0.01, 0.02, 0.01, 0.01, 0.02, 0.01, 0.05],
    [0.10, 0.01, 0.05, 0.02, 0.02, 0.05, 0.01, 0.10],
    [-.25, -.25, 0.01, 0.01, 0.01, 0.01, -.25, -.25],
    [1.00, -.25, 0.10, 0.05, 0.05, 0.10, -.25, 1.00]]

class Node:
    def __init__(self,inmat,turn,location_moved):
        self.data = inmat.copy()
        self.turn = turn
        self.new_piece = location_moved
        self.terminal = False
        self.heur = self.__heur()
        self.depth = None
        self.value = None
        self.type = None

    def __len__(self):
        return 1

    def __eq__(self, other):
        return numpy.array_equal(self.data, other.data)

    def __hash__(self):
        return hash(str(self.data))

    def __heur(self):
        winner = check4win(self.data)
        if winner:
            self.terminal = True
            return winner*float('inf') if winner == 1 or winner == -1 else 0

        h = 0
        # [r,c] = numpy.where(self.data==1)
        # for i in xrange(len(r)):
        #     h += fabs(3.5-r[i])*4+fabs(3.5-c[i])*4
        # [r,c] = numpy.where(self.data==-1)
        # for i in xrange(len(r)):
        #     h -= fabs(3.5-r[i])*4+fabs(3.5-c[i])*4
        
        # h += 20*len(numpy.where(self.data[[0,0,-1,-1],[0,-1,0,-1]]==1)[0])
        # h += 10*len(numpy.where(self.data[0,:]==1)[0])
        # h += 10*len(numpy.where(self.data[:,0]==1)[0])
        # h += 10*len(numpy.where(self.data[-1,:]==1)[0])
        # h += 10*len(numpy.where(self.data[:,-1]==1)[0])
        # h += len(numpy.where(self.data==1)[0])

        # h -= 20*len(numpy.where(self.data[[0,0,-1,-1],[0,-1,0,-1]]==-1)[0])
        # h -= 10*len(numpy.where(self.data[0,:]==-1)[0])
        # h -= 10*len(numpy.where(self.data[:,0]==-1)[0])
        # h -= 10*len(numpy.where(self.data[-1,:]==-1)[0])
        # h -= 10*len(numpy.where(self.data[:,-1]==-1)[0])
        # h -= len(numpy.where(self.data==-1)[0])
        h = -self.turn*board_h[self.new_piece[0]][self.new_piece[1]]
        
        return h


def move_indexes(board,player):
    [r,c] = numpy.where(board==player)
    validmoves = []
    for i in xrange(len(r)):
        for dir1,dir2 in steps:
            if r[i]+dir1 >= 0 and r[i]+dir1 < len(board) and c[i]+dir2 >= 0 and c[i]+dir2 < len(board[0]) and board[r[i]+dir1,c[i]+dir2] == -player:
                cnt = 2
                while r[i]+cnt*dir1 in range(len(board)) and c[i]+cnt*dir2 in range(len(board[0])) and board[r[i]+cnt*dir1,c[i]+cnt*dir2] != player:
                    if board[r[i]+cnt*dir1,c[i]+cnt*dir2] == 0:
                        validmoves.append([r[i]+cnt*dir1,c[i]+cnt*dir2])
                        break
                    cnt += 1
    validmoves = [list(x) for x in set(tuple(x) for x in validmoves)]
    return validmoves

def playermove(board,player,r,c):
    brd = board.copy()
    brd[r][c] = player
    for dir1,dir2 in steps:
        [v,temp] = _flip_until_end(brd,player,r+dir1,c+dir2,dir1,dir2)
        if v:
            brd = temp
    return Node(brd,-player,(r,c))

def _flip_until_end(brd,player,r,c,x,y):
    if r < 0 or r >= len(brd) or c < 0 or c >= len(brd[0]) or brd[r][c] == 0:
        return [0,brd]
    elif brd[r][c] == player:
        return [1,brd]
    [v,brd] = _flip_until_end(brd,player,r+x,c+y,x,y)
    if v:
        brd[r][c] = player
        return [1,brd]
    return [0,brd]
    
def neighbor_nodes(board,player):
    validmoves = move_indexes(board,player)
    for move in validmoves:
        yield playermove(board,player,move[0],move[1])


def alpha_beta_memory(n,alpha,beta,d):
    global visited_states
    if visited_states.get(n) and visited_states[n].depth >= d:
        tte = visited_states.get(n)
        if tte.type == 'exact':
            return tte.value
        if tte.type == 'lower' and tte.value > alpha:
            alpha = tte.value
        elif tte.type == 'upper' and tte.value < beta:
            beta = tte.value
        if alpha >= beta:
            return tte.value
    if d == 0 or n.terminal:
        g = n.heur
    elif n.turn == 1:
        g = -float('inf')
        a = alpha
        children = neighbor_nodes(n.data,n.turn)
        c = next(children, None)
        while g < beta and c:
            g = max(g, alpha_beta_memory(c, a, beta, d-1))
            a = max(a, g)
            c = next(children, None)
    else:
        g = float('inf')
        b = beta
        children = neighbor_nodes(n.data,n.turn)
        c = next(children, None)
        while g > alpha and c:
            g = min(g, alpha_beta_memory(c, alpha, b, d-1))
            b = min(b, g)
            c = next(children, None)
    if g <= alpha:
        n.type = 'lower'
    elif g >= beta:
        n.type = 'upper'
    else:
        n.type = 'exact'
    n.value = g
    n.depth = d
    visited_states[n] = n
    return g


def mtdf(root, f, d):
    g = f
    upperbound = float('inf')
    lowerbound = -float('inf')
    while lowerbound < upperbound:
        if g == lowerbound:
            beta = g+1
        else:
            beta = g
        g = alpha_beta_memory(root, beta-1, beta, d)
        if g < beta:
            upperbound = g
        else:
            lowerbound = g
    return g


def check4win(b):
    hmoves = move_indexes(b,human_num)
    cmoves = move_indexes(b,comp_num)
    if hmoves or cmoves:
        return 0
    hums = len(numpy.where(b==human_num)[0])
    comps = len(numpy.where(b==comp_num)[0])
    if hums > comps:
        return 1
    elif comps > hums:
        return -1
    else:
        return 3


global visited_states
visited_states = {}

def computermove(board):
    if generate:
        global visited_states
        alpha_beta_memory(Node(board,1), -float('inf'), float('inf'), -1)
        with open('maxfirst','w') as f:
            l = [val.__dict__ for _,val in visited_states.items()]
            pickle.dump(l,f,-1)
        visited_states = {}
        alpha_beta_memory(Node(board,-1), -float('inf'), float('inf'), -1)
        with open('minfirst','w') as f:
            l = [val.__dict__ for _,val in visited_states.items()]
            pickle.dump(l,f,-1)
        return
    
    x = time.time()
    depth = 5
    children = [i for i in neighbor_nodes(board,comp_num)]
    if not children:
        print 'Computer cannot move'
        return board

    moves = []
    
    for child in children:
        first_guess = 0
        for d in xrange(1,depth):
            first_guess = mtdf(child, first_guess, d)
        moves.append(first_guess)
    optimal_move = children[numpy.argmin(moves)]

    print 'Elapsed time is {0} seconds'.format(time.time()-x)
    print ' '
    print_board(optimal_move.data)
    return optimal_move.data

def print_board(board):
    output = []
    output.append('  '.join(str(i) for i in xrange(len(board[0]))))
    output[0] = '    '+output[0]
    for i in xrange(len(board)):
        output.append(' '.join([str(i),str(board[i]).replace('-1',' W').replace('1','B').replace('0',' ').replace('.','')]))
    print '\n'.join(output)

def main():
    board = numpy.zeros(64).reshape((8,8))
    board[3][3] = -1
    board[3][4] = 1
    board[4][3] = 1
    board[4][4] = -1

    if generate:
        computermove(board)
        return
    
    print_board(board)
    while True:
        usermoves = move_indexes(board,human_num)
        print ' '
        print 'Valid moves are: '+str(usermoves)
        usermove = raw_input('Enter row and col separated by space: ')
        usermove = usermove.split(' ')
        for i in xrange(len(usermove)):
            usermove[i] = int(usermove[i])
        if not usermove in usermoves:
            print 'Invalid choice'
            continue
        board = playermove(board, human_num, usermove[0], usermove[1]).data
        print ' '
        print_board(board)
        won = check4win(board)
        if won:
            if won == human_num:
                print 'Human won'
            elif won == comp_num:
                print 'Computer won'
            else:
                print 'Tie'
            return
        print 'Computer is attempting to move...'
        board = computermove(board)
        won = check4win(board)
        if won:
            print 'Human: ' + str(len(numpy.where(board==human_num)[0]))
            print 'Computer: ' + str(len(numpy.where(board==comp_num)[0]))
            if won == human_num:
                print 'Human won'
            elif won == comp_num:
                print 'Computer won'
            else:
                print 'Tie'
            return
        usermoves = move_indexes(board, human_num)
        while not usermoves:
            print 'Human cannot move'
            board = computermove(board)
            won = check4win(board)
            if won:
                if won == human_num:
                    print 'Human won'
                elif won == comp_num:
                    print 'Computer won'
                else:
                    print 'Tie'
                return
            usermoves = move_indexes(board, human_num)

        
if __name__ == '__main__':
    main()
