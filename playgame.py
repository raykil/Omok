"""
    This function controls the overall process of the game. The algorithm is to be drawn.
"""

import brain
import pygame
from display import Board
from optparse import OptionParser

parser = OptionParser(usage="%prog [options]")
parser.add_option('--AiMode'  , dest='AiMode'  , default=False, action='store_true')
parser.add_option('--MyPlayer', dest='MyPlayer', default=1    , type=int, help='only meaningful if AiMode is activated. 1 means black, -1 means white.')
(options, args) = parser.parse_args()
AiMode   = options.AiMode
MyPlayer = options.MyPlayer

def Process():
    board = Board(nCell=15, AiMode=AiMode, MyPlayer=MyPlayer)
    board.DisplayScreen()
    while True:
        board.BlackScore = brain.CalculateScore(board, 'Black')
        board.WhiteScore = brain.CalculateScore(board, 'White')
        if   board.BlackScore==5: board.is_terminal=True
        elif board.WhiteScore==5: board.is_terminal=True

        AiTurn = True if (MyPlayer==1 and len(board.EventTracker)%2==1)|(MyPlayer==-1 and len(board.EventTracker)%2==0) else False
        if AiMode and AiTurn: 
            NextMove = brain.GetNextMove(board)
            board.PlaceStone(NextMove)
            board.DisplayBoard()
        else: 
            board.DisplayBoard()
            grid_out, stone_exists, undo_pressed, valid_input, board.gridloc = board.GetInput()
            if   undo_pressed: board.RemoveStone()
            elif grid_out    : board.DisplayBoard()
            elif stone_exists: board.DisplayBoard()
            elif valid_input : board.PlaceStone(board.gridloc)

pygame.init()
Process()