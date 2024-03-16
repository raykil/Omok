import brain
import pygame
import numpy as np
from sys import exit
from random import randint

class Board:
    def __init__(self, nCell=15, AiMode=True, MyPlayer=1):
        # frontend attributes
        self.nCell        = nCell
        self.unit         = 40
        self.length       = (nCell+3) * 40 # length of the board
        self.screenLength = (nCell+5) * 40 # length of the screen
        self.board        = pygame.Surface((self.length, self.length))

        # backend attributes
        self.AiMode       = AiMode
        self.MyPlayer     = MyPlayer
        self.BoardTracker = np.array([[0]*nCell+[2]*4] * nCell + [[2]*(nCell+4)] * 4)
        self.EventTracker = []
        self.BlackScore   = 0
        self.WhiteScore   = 0
        self.is_terminal  = False
        self.grid_out     = False
        self.stone_exists = False
        self.clock        = pygame.time.Clock()

        # game initialization
        self.PlaceStone((self.nCell//2,self.nCell//2)) # Place a black stone at the center

    def DisplayScreen(self):
        self.screen = pygame.display.set_mode((self.screenLength, self.screenLength))
        pygame.display.set_caption("Omok")
        self.screen.fill('gray17')

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
        undoButton = pygame.Rect(self.unit*2, self.unit*(self.nCell+1.5), self.unit*3, self.unit)
        pygame.draw.rect(self.board, 'grey50', undoButton)
        self.undoLoc, self.undoSize = np.array(undoButton.topleft)+self.unit, np.array(undoButton.size)
        undoText = pygame.font.Font(None, int(0.8*self.unit)).render("Undo", True, 'black')
        undoRect = undoText.get_rect(center=undoButton.center)
        self.board.blit(undoText, undoRect)

        ### COUNTER ###
        player = 'Black' if len(self.EventTracker)%2==0 else 'White'
        self.counterfont = pygame.font.Font(None, int(0.8*self.unit))
        if not self.is_terminal: self.board.blit(self.counterfont.render(f"Count: {len(self.EventTracker)}, {player}'s turn", True, 'grey8'),(0.3*self.length, 0.02*self.length))
        else: self.board.blit(self.counterfont.render(f"Count: {len(self.EventTracker)}", True, 'grey8'),(0.4*self.length, 0.02*self.length))
        
        ### STONES ###
        for idx, gridloc in enumerate(self.EventTracker):
            color = 'grey8' if idx%2==0 else 'grey97'
            pygame.draw.circle(self.board, color, ((gridloc[1]+2)*40, (gridloc[0]+2)*40), radius=16)
        
        ### MESSAGES ###
        if self.is_terminal:
            terminal_font = pygame.font.Font(None, 40)
            terminal_state = terminal_font.render(f"Terminal state. {'White' if len(self.EventTracker)%2==0 else 'Black'} won!", True, "firebrick2")
            self.board.blit(terminal_state,(5.5*self.unit, 16.75*self.unit))
        
        elif self.grid_out:
            gridout_font = pygame.font.Font(None, 30)
            gridout_state = gridout_font.render(f"Selected location is outside the grid.", True, "gray24")
            self.board.blit(gridout_state,(5.5*self.unit, 16.75*self.unit))
        
        elif self.stone_exists:
            exist_font  = pygame.font.Font(None, 30)
            exist_state = exist_font.render(f"Stone already exists. Place it somewhere else.", True, "gray24")
            self.board.blit(exist_state,(5.5*self.unit, 16.75*self.unit))

    def GetInput(self):
        self.undo_pressed, self.valid_input = False, False
        while (not self.undo_pressed)|(not self.valid_input):
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit(); exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        self.gridloc      = (round(pygame.mouse.get_pos()[1]/self.unit-3), round(pygame.mouse.get_pos()[0]/self.unit-3))
                        self.undo_pressed = (pygame.mouse.get_pos()[0] >= self.undoLoc[0])&(pygame.mouse.get_pos()[0] <= self.undoLoc[0]+self.undoSize[0])&(pygame.mouse.get_pos()[1] >= self.undoLoc[1])&(pygame.mouse.get_pos()[1] <= self.undoLoc[1]+self.undoSize[1])
                        self.grid_out     = ((self.gridloc[0] >= 15)|(self.gridloc[1] >= 15)|(self.gridloc[0] < 0)|(self.gridloc[1] < 0))&(not self.undo_pressed)
                        self.stone_exists = (self.BoardTracker[self.gridloc[0]][self.gridloc[1]] != 0)&(not self.undo_pressed)
                        self.valid_input  = ~(self.BoardTracker[self.gridloc[0]][self.gridloc[1]])
                        return self.grid_out, self.stone_exists, self.undo_pressed, self.valid_input, self.gridloc

            self.screen.blit(self.board, (self.unit, self.unit))
            pygame.display.update()
            self.clock.tick(24)

    def PlaceStone(self, gridloc):
        self.BoardTracker[gridloc[0]][gridloc[1]] = 1-2*(len(self.EventTracker)%2) # 1 for black, -1 for white
        self.EventTracker.append(gridloc)

    def RemoveStone(self):
        self.BoardTracker[self.EventTracker[-1][0]][self.EventTracker[-1][1]] = 0
        self.EventTracker = self.EventTracker[:-1]
        self.is_terminal = False