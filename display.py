import pygame
import numpy as np
from sys import exit
import brain

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
            pygame.draw.circle(self.board, color, ((gridloc[0]+2)*40, (gridloc[1]+2)*40), radius=16)

    def GetInput(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        self.gridloc = tuple(np.array(np.round(np.array(pygame.mouse.get_pos())/board.unit)-3,dtype=int))
                        undo_pressed = (pygame.mouse.get_pos()[0] >= board.undoLoc[0])&(pygame.mouse.get_pos()[0] <= board.undoLoc[0]+board.undoSize[0])&(pygame.mouse.get_pos()[1] >= board.undoLoc[1])&(pygame.mouse.get_pos()[1] <= board.undoLoc[1]+board.undoSize[1])
                        grid_out = (self.gridloc[1] >= 15)|(self.gridloc[0] >= 15)|(self.gridloc[1] < 0)|(self.gridloc[0] < 0)

                        if undo_pressed: self.RemoveStone() # clicked undo button
                        elif grid_out: print("Selected location is outside the grid.") # clicked ouside the grid
                        elif board.BoardTracker[self.gridloc[1]][self.gridloc[0]] != 0: print("Stone already exists. Place it somewhere else.") # clicked where a stone exists
                        elif ~(board.BoardTracker[self.gridloc[1]][self.gridloc[0]]): self.PlaceStone(self.gridloc) # clicked the correct spot for a stone
            self.screen.blit(self.board, (self.unit, self.unit))
            pygame.display.update()
            self.clock.tick(24)

    def PlaceStone(self, gridloc):
        # place stone on the board
        self.BoardTracker[gridloc[1]][gridloc[0]] = 1-2*(len(self.EventTracker)%2) # 1 for black, -1 for white
        self.EventTracker.append(gridloc)
        self.DisplayBoard()
        
        # count
        self.b_ones, self.b_twos, self.b_tres, self.b_furs, self.b_fivs, self.b_sixs, self.b_sevs = brain.count(1 , self.BoardTracker) # count for black
        self.w_ones, self.w_twos, self.w_tres, self.w_furs, self.w_fivs, self.w_sixs, self.w_sevs = brain.count(-1, self.BoardTracker) # count for white
        
        # terminal state checking
        if   len(self.EventTracker)%2==1: terminal_state = self.IsTerminal(self.b_fivs, 'Black')
        elif len(self.EventTracker)%2==0: terminal_state = self.IsTerminal(self.w_fivs, 'White')
        
        # calculate score of the current board
        if not terminal_state: b_CurrentScore, w_CurrentScore = self.CalculateScore()

        # wait for next input
        self.GetInput()
    
    def RemoveStone(self):
        self.BoardTracker[self.EventTracker[-1][1]][self.EventTracker[-1][0]] = 0
        self.EventTracker = self.EventTracker[:-1]
        board.DisplayBoard()

    def CalculateScore(self):
        print(f'\n----------count: {len(self.EventTracker)}----------')
        b_CurrentScore, w_CurrentScore = 0, 0
        
        # calculate Black's score of the current board
        if len(self.b_ones): b_ones_sickness = brain.SicknessTest(self.b_ones, self.BoardTracker)[1]; b_ones_ScoreDict = brain.AssignScore(self.b_ones, b_ones_sickness, 'Black'); b_CurrentScore += b_ones_ScoreDict['NormalScore']
        if len(self.b_twos): b_twos, b_twos_sickness = brain.SicknessTest(self.b_twos, self.BoardTracker); b_twos_ScoreDict = brain.AssignScore(b_twos, b_twos_sickness, 'Black'); b_CurrentScore += b_twos_ScoreDict['NormalScore']
        if len(self.b_tres): b_tres, b_tres_sickness = brain.SicknessTest(self.b_tres, self.BoardTracker); b_tres_ScoreDict = brain.AssignScore(b_tres, b_tres_sickness, 'Black'); b_CurrentScore += b_tres_ScoreDict['NormalScore']
        if len(self.b_furs): b_furs, b_furs_sickness = brain.SicknessTest(self.b_furs, self.BoardTracker); b_furs_ScoreDict = brain.AssignScore(b_furs, b_furs_sickness, 'Black'); b_CurrentScore += b_furs_ScoreDict['NormalScore']

        # calculate White's score of the current board
        if len(self.w_ones): w_ones_sickness = brain.SicknessTest(self.w_ones, self.BoardTracker)[1]; w_ones_ScoreDict = brain.AssignScore(self.w_ones, w_ones_sickness, 'White'); w_CurrentScore += w_ones_ScoreDict['NormalScore']
        if len(self.w_twos): w_twos, w_twos_sickness = brain.SicknessTest(self.w_twos, self.BoardTracker); w_twos_ScoreDict = brain.AssignScore(w_twos, w_twos_sickness, 'White'); w_CurrentScore += w_twos_ScoreDict['NormalScore']
        if len(self.w_tres): w_tres, w_tres_sickness = brain.SicknessTest(self.w_tres, self.BoardTracker); w_tres_ScoreDict = brain.AssignScore(w_tres, w_tres_sickness, 'White'); w_CurrentScore += w_tres_ScoreDict['NormalScore']
        if len(self.w_furs): w_furs, w_furs_sickness = brain.SicknessTest(self.w_furs, self.BoardTracker); w_furs_ScoreDict = brain.AssignScore(w_furs, w_furs_sickness, 'White'); w_CurrentScore += w_furs_ScoreDict['NormalScore']

        print(f"Black's score: {b_CurrentScore}")
        print(f"White's score: {w_CurrentScore}")
        return b_CurrentScore, w_CurrentScore

    def IsTerminal(self, fivs, player):
        is_terminal = brain.IsTerminal(fivs)
        if is_terminal:
            print(f"Terminal state. {player} won!")
            terminal_font = pygame.font.Font(None, 40)
            terminal_state = terminal_font.render(f"Terminal state. {player} won!", True, "firebrick2")
            self.board.blit(terminal_state,(5*self.unit, 17*self.unit))
            return True
        return False

board = Board()
board.DisplayScreen()