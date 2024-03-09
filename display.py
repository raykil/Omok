import brain
import pygame
import numpy as np
from sys import exit
from random import randint
from optparse import OptionParser

parser = OptionParser(usage="%prog [options]")
parser.add_option('--AiMode'  , dest='AiMode'  , default=False, action='store_true')
parser.add_option('--MyPlayer', dest='MyPlayer', default=1    , type=int, help='only meaningful if AiMode is activated. 1 means black, -1 means white.')
(options, args) = parser.parse_args()

AiMode   = options.AiMode
MyPlayer = options.MyPlayer
pygame.init()

class Board:
    def __init__(self, nCell=15):
        self.nCell        = nCell
        self.unit         = 40
        self.length       = (nCell+3) * 40 # length of the board
        self.screenLength = (nCell+5) * 40 # length of the screen
        self.board        = pygame.Surface((self.length, self.length))
        self.BoardTracker = np.array([[0]*nCell+[2]*4] * nCell + [[2]*(nCell+4)] * 4)
        self.EventTracker = []
        self.clock        = pygame.time.Clock()

    def DisplayScreen(self):
        self.screen = pygame.display.set_mode((self.screenLength, self.screenLength))
        pygame.display.set_caption("Omok")
        self.screen.fill('gray17')
        self.DisplayBoard()

    def DisplayBoard(self):
        ### BOARD ###
        background = pygame.image.load("/Users/raymondkil/Desktop/omok/boardbg.jpg")
        self.board.blit(background,(0,0))
        for n in range(self.nCell):
            # grid lines
            pygame.draw.line(self.board, 'grey8', (2.0*self.unit, (2.0+n)*self.unit), (self.length-2.0*self.unit, (2.0+n)*self.unit), width=2) # row
            pygame.draw.line(self.board, 'grey8', ((2.0+n)*self.unit, 2.0*self.unit), ((2.0+n)*self.unit, self.length-2.0*self.unit), width=2) # col
            
            # coordinate numbers
            coordfont = pygame.font.Font(None, int(0.8*self.unit))
            coords = coordfont.render(str(n), True, 'lightsalmon4')
            self.board.blit(coords,(1.1*self.unit, (1.8+n)*self.unit)) # row
            self.board.blit(coords,((1.7+n)*self.unit, 1.2*self.unit)) # col

        # pivot points
        pygame.draw.circle(self.board, 'grey8', ((self.nCell-10)*self.unit, (self.nCell-10)*self.unit), radius=5)
        pygame.draw.circle(self.board, 'grey8', ((self.nCell-10)*self.unit, (self.nCell-2 )*self.unit), radius=5)
        pygame.draw.circle(self.board, 'grey8', ((self.nCell-2 )*self.unit, (self.nCell-10)*self.unit), radius=5)
        pygame.draw.circle(self.board, 'grey8', ((self.nCell-2 )*self.unit, (self.nCell-2 )*self.unit), radius=5)

        ### UNDO BUTTON ###
        undoButton = pygame.Rect(self.unit*2, self.unit*16.5, self.unit*3, self.unit)
        pygame.draw.rect(self.board, 'grey50', undoButton)
        undoText = pygame.font.Font(None, int(0.8*self.unit)).render("Undo", True, 'black')
        self.undoLoc, self.undoSize = np.array(undoButton.topleft)+self.unit, np.array(undoButton.size)
        self.undoRect = undoText.get_rect(center=undoButton.center)
        self.board.blit(undoText, self.undoRect)

        ### COUNTER ###
        player = 'Black' if len(self.EventTracker)%2==0 else 'White'
        self.counterfont = pygame.font.Font(None, int(0.8*self.unit))
        self.board.blit(self.counterfont.render(f"count: {len(self.EventTracker)}, {player}'s turn", True, 'grey8'),(0.3*self.length, 0.02*self.length))

        # initiate game by placing black stone at the center
        if not len(self.EventTracker): self.PlaceStone((7,7))
        
        ### STONES ###
        for idx, gridloc in enumerate(self.EventTracker):
            color = 'grey8' if idx%2==0 else 'grey97'
            pygame.draw.circle(self.board, color, ((gridloc[1]+2)*40, (gridloc[0]+2)*40), radius=16)

    def GetInput(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        self.gridloc = (round(pygame.mouse.get_pos()[1]/self.unit-3), round(pygame.mouse.get_pos()[0]/self.unit-3))
                        undo_pressed = (pygame.mouse.get_pos()[0] >= board.undoLoc[0])&(pygame.mouse.get_pos()[0] <= board.undoLoc[0]+board.undoSize[0])&(pygame.mouse.get_pos()[1] >= board.undoLoc[1])&(pygame.mouse.get_pos()[1] <= board.undoLoc[1]+board.undoSize[1])
                        grid_out = (self.gridloc[0] >= 15)|(self.gridloc[1] >= 15)|(self.gridloc[0] < 0)|(self.gridloc[1] < 0)

                        if undo_pressed: self.RemoveStone() # clicked undo button
                        elif grid_out: print("Selected location is outside the grid.") # clicked ouside the grid
                        elif self.BoardTracker[self.gridloc[0]][self.gridloc[1]] != 0: print("Stone already exists. Place it somewhere else.") # clicked where a stone exists
                        elif ~(self.BoardTracker[self.gridloc[0]][self.gridloc[1]]): self.PlaceStone(self.gridloc) # clicked the correct spot for a stone
            self.screen.blit(self.board, (self.unit, self.unit))
            pygame.display.update()
            self.clock.tick(24)

    def PlaceStone(self, gridloc):
        # place stone on the board
        self.BoardTracker[gridloc[0]][gridloc[1]] = 1-2*(len(self.EventTracker)%2) # 1 for black, -1 for white
        self.EventTracker.append(gridloc)
        self.DisplayBoard()
        
        # count
        self.b_ones, self.b_twos, self.b_tres, self.b_furs, self.b_fivs, self.b_sixs, self.b_sevs = brain.count(1 , self.BoardTracker) # count for black
        self.w_ones, self.w_twos, self.w_tres, self.w_furs, self.w_fivs, self.w_sixs, self.w_sevs = brain.count(-1, self.BoardTracker) # count for white
        
        # terminal state checking
        if   len(self.EventTracker)%2==1: is_terminal = brain.IsTerminal(board, 'Black')
        elif len(self.EventTracker)%2==0: is_terminal = brain.IsTerminal(board, 'White')
        
        # calculate score of the current board
        if not is_terminal: 
            self.BlackScore = brain.AssignScore(board, 'Black')
            self.WhiteScore = brain.AssignScore(board, 'White')

        # wait for next input
        if not AiMode: self.GetInput()
        elif (len(self.EventTracker)%2==0 and MyPlayer==-1 and not is_terminal) | (len(self.EventTracker)%2==1 and MyPlayer==1 and not is_terminal): self.AiPlaceStone()
        else: self.GetInput()
    
    def RemoveStone(self):
        self.BoardTracker[self.EventTracker[-1][1]][self.EventTracker[-1][0]] = 0
        self.EventTracker = self.EventTracker[:-1]
        board.DisplayBoard()

    def AiPlaceStone(self):
        self.EventCands = brain.GetEventCand(board)
        NextMove = brain.Minimax(board)
        self.PlaceStone(self.EventCands[randint(0,len(self.EventCands)-1)])
        #self.PlaceStone(NextMove)

board = Board()
board.DisplayScreen()