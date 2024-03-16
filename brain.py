import numpy as np
from random import randint
from collections import Counter

def count(board, player, space_allowed=2, debug=False):
    """
        This function counts and returns the number of 1s, 2s, 3s, 4s, and 5s of a player.
        Inputs: board is the board object, player is either 'Black' or 'White'. Translated into 1 or -1 inside the function.
        Notes on variables:
          - 'playerstones' is a list containing tuples that represent all stones placed by a player.
          - 'directions' represens row-col indices relative to pivot stone in the order of (northwest-southeast), (north-south), (northeast-southwest), and (west-east).
          - 'connected' stores group of connected stone indices at the same index as 'directions'. Ex) [[], [(8, 6), (9, 6)], [], [(7, 7)]] -> nn-ss (three), ww-ee (two) are connected.
          - 'space' variables are integers that represent consecutive spaces within connections. 
          - 'stones' is a list of tuples that stores the group of connected stones in one direction.
          - 'space_allowed' is an integer representing spaces allowed within a connection.
    """
    if debug: print('')
    player = 1 if player=='Black' else -1

    # gathering player stones
    playerstones = []
    for row in range(len(board.BoardTracker)):
        for col in range(len(board.BoardTracker[0])):
            if board.BoardTracker[row][col] == player: 
                playerstones.append((row,col))

    ones, twos, tres, furs, fivs, sixs, sevs = [],[],[],[],[],[],[]
    directions = [(-1,-1,1,1), (-1,0,1,0), (-1,1,1,-1), (0,-1,0,1)]
    
    # count for each stone
    for stone in playerstones:
        r, c, connected = stone[0], stone[1], []
        
        # for each direction
        for direction in directions:
            stones, space1, space2 = [], 0, 0

            # "upper" directions
            for n in range(1,7):
                if board.BoardTracker[r+direction[0]*n][c+direction[1]*n] == player: stones.append((r+direction[0]*n, c+direction[1]*n))
                elif (board.BoardTracker[r+direction[0]*n][c+direction[1]*n] == 0) & (space1 < space_allowed): space1 += 1
                else: break
                
            # "lower" directions
            for n in range(1,7):
                if board.BoardTracker[r+direction[2]*n][c+direction[3]*n] == player: stones.append((r+direction[2]*n, c+direction[3]*n))
                elif (board.BoardTracker[r+direction[2]*n][c+direction[3]*n] == 0) & (space2 < space_allowed): space2 += 1
                else: break
            
            connected.append(stones)
        
        if debug: print(f'{stone}: {connected}')
        for dir in connected:
            if len(dir) == 0 and [stone] not in ones and not any([len(c) for c in connected]): ones.append([stone])
            elif len(dir) == 1 and all([False if Counter(dir+[stone])==Counter(two) else True for two in twos]): twos.append(dir+[stone])
            elif len(dir) == 2 and all([False if Counter(dir+[stone])==Counter(tre) else True for tre in tres]): tres.append(dir+[stone])
            elif len(dir) == 3 and all([False if Counter(dir+[stone])==Counter(fur) else True for fur in furs]): furs.append(dir+[stone])
            elif len(dir) == 4 and all([False if Counter(dir+[stone])==Counter(fiv) else True for fiv in fivs]): fivs.append(dir+[stone])
            elif len(dir) == 5 and all([False if Counter(dir+[stone])==Counter(six) else True for six in sixs]): sixs.append(dir+[stone])
            elif len(dir) == 6 and all([False if Counter(dir+[stone])==Counter(sev) else True for sev in sevs]): sevs.append(dir+[stone])

    # sorting into increasing row/col order
    if len(twos): twos = [sorted(two, key=lambda x: (x[0], x[1])) for two in twos]
    if len(tres): tres = [sorted(tre, key=lambda x: (x[0], x[1])) for tre in tres]
    if len(furs): furs = [sorted(fur, key=lambda x: (x[0], x[1])) for fur in furs]
    if len(fivs): fivs = [sorted(fiv, key=lambda x: (x[0], x[1])) for fiv in fivs]
    if len(sixs): sixs = [sorted(six, key=lambda x: (x[0], x[1])) for six in sixs]
    if len(sevs): sevs = [sorted(sev, key=lambda x: (x[0], x[1])) for sev in sevs]
    if debug: print(f'ones: {ones}\ntwos: {twos}\ntres: {tres}\nfurs: {furs}\nfivs: {fivs}\nsixs: {sixs}\nsevs: {sevs}\n')    
    return {'ones': ones, 'twos': twos, 'tres': tres, 'furs': furs, 'fivs': fivs, 'sixs': sixs, 'sevs': sevs}

def SicknessTest(connections, board):
    """
        This function performs what I call the 'sickness test'.
        Any connection of length at least 2 has two endpoints called edge1 (the one with lower row/col value) and edge2 (the one with greater row/col value).
        The process of checking if each endpoint of a connection is blocked by the opponent is called the 'sickness test'.
        I call the connections that are open on both endpoints 'live', those blocked on one side 'sick', and those blocked on both sides 'dead'.
        The function returns a dictionary.

        Notes on 'sickness_value': default open space is both side open (thus 2), gets subtracted whenever an edge is blocked.
    """
    sickness = []
    for ns in connections:
        if len(connections[0])==1: 
            r, c = ns[0][0], ns[0][1]
            sickness_value = [
                board.BoardTracker[r-1][c-1], board.BoardTracker[r-1][c+0], board.BoardTracker[r-1][c+1],
                board.BoardTracker[r+0][c-1]                              , board.BoardTracker[r+0][c+1],
                board.BoardTracker[r+1][c-1], board.BoardTracker[r+1][c+0], board.BoardTracker[r+1][c+1],
            ].count(0)*0.125
            
        else:
            sickness_value = 2
            dir_r, dir_c = ns[1][0] - ns[0][0], ns[1][1] - ns[0][1]
            edge1, edge2 = ns[0], ns[-1]
        
            # testing edge1
            if board.BoardTracker[edge1[0]-dir_r][edge1[1]-dir_c]==0: pass
            else: sickness_value -= 1
            
            # testing edge2
            if board.BoardTracker[edge2[0]+dir_r][edge2[1]+dir_c]==0: pass
            else: sickness_value -= 1

        sickness.append(sickness_value)
    return sickness

def CalculateScore(board, player, debug=False):
    """
        This function calculates and assigns a player's current normalized score.
        This function contains parameters whose values must be tested and optimized (machine learning?).
        The parameters are:
          - 'key'        : the id for the keys of the raw_score_scheme ('ones', 'twos', 'tres', 'furs'). Used to simplify the loop.
          - 'raw_score'  : a real number that represents the score of a connection that adds up without any normalization or optimization.
          - 'sick_factor': a factor multiplied to 'raw_score' to give penalty to sick connections.
          - 'dead_factor': a factor multiplied to 'raw_score' to give penalty to dead (can easily think dead as *0, but maybe not!) connections. 
          - 'amplitude'  : the converging value of (amplitude)*arctan(n)*(2/pi) as n goes to infinity. 
                           This parameter sets the maximum limit of score contribution by a group of n-connections.
          - 'steepness'  : a value specifying how steep the arctan graph will approach the asymptotic value. 
                           Big changes according to steepness happens at lower x values, while the number of n-connections lie in the region where big changes happen.
                           Thus, this parameter might give significant change.
        This function returns the score (a float) for a player.
    """
    ScoreParams = { # can black and white be different?
        'ones': {'raw_score': 1, 'sick_factor': 1/2, 'dead_factor': 0.0, 'amplitude': 0.5, 'steepness': 1.0},
        'twos': {'raw_score': 2, 'sick_factor': 1/2, 'dead_factor': 0.0, 'amplitude': 1.0, 'steepness': 2.5},
        'tres': {'raw_score': 3, 'sick_factor': 2/3, 'dead_factor': 0.0, 'amplitude': 1.5, 'steepness': 4.0},
        'furs': {'raw_score': 4, 'sick_factor': 3/4, 'dead_factor': 0.0, 'amplitude': 2.0, 'steepness': 5.5},
    }
    #CountsDict = count(player, board.BoardTracker)
    CountsDict = count(board, player)
    ones, twos, tres, furs, fivs = CountsDict['ones'], CountsDict['twos'], CountsDict['tres'], CountsDict['furs'], CountsDict['fivs']

    #print(f'hello I am player {player}: \nones:{ones}\ntwos:{twos}\ntres:{tres}\nfurs:{furs}\nfivs:{fivs}\n')
    if len(fivs): return 5.0
    else:
        TotalRawScore, TotalNormalScore = 0, 0
        if debug: table = PrettyTable(); table.field_names = [f"Connections (Round{len(board.EventTracker)}, {player})", "Raw Score", "Normal Score"]
        
        for ns, n_param in zip([ones, twos, tres, furs], ScoreParams.keys()):
            sickness  = SicknessTest(ns, board)
            amplitude, steepness = ScoreParams[n_param]['amplitude'], ScoreParams[n_param]['steepness']
            
            if len(ns) and len(ns[0])==1: # if doing ones...
                RawScore    = sum(sickness)
                NormalScore = amplitude * np.arctan(steepness*RawScore) * 2/np.pi
            else:
                raw_score, sick_factor, dead_factor = ScoreParams[n_param]['raw_score'], ScoreParams[n_param]['sick_factor'], ScoreParams[n_param]['dead_factor']
                RawScore    = raw_score*sickness.count(2) + raw_score*sickness.count(1)*sick_factor + raw_score*sickness.count(0)*dead_factor
                NormalScore = amplitude * np.arctan(steepness*RawScore) * 2/np.pi
            
            if debug: table.add_row([n_param, RawScore, NormalScore])
            TotalRawScore    += RawScore
            TotalNormalScore += NormalScore
        if debug: table.add_row(['Total', TotalRawScore, TotalNormalScore]); print(table)
        return TotalNormalScore

def GetEventCand(board, max_space=2, debug=False):
    EventCands = []
    if debug: print(f'----------event {len(board.EventTracker)}----------')
    for stone in board.EventTracker:
        for r in range(-max_space,max_space+1):
            for c in range(-max_space,max_space+1):
                if debug: print(f'for stone {stone} -- place to test: {stone[0]+r}, {stone[1]+c}, what is on it: {board.BoardTracker[stone[0]+r][stone[1]+c]}')
                if board.BoardTracker[stone[0]+r][stone[1]+c]==0 and (stone[0]+r,stone[1]+c) not in EventCands: EventCands.append((stone[0]+r,stone[1]+c))
    EventCands = sorted(EventCands)
    if debug: print("EventCands: ", EventCands)
    return EventCands

def GetNextMove(board):
    eventcands = GetEventCand(board)
    return eventcands[randint(0,len(eventcands)-1)]