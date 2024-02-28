from collections import Counter

def count(player, BoardTracker, space_allowed=2, debug=False):
    """
        counts and returns the number of 1s, 2s, 3s, 4s, and 5s of a player.
        player is represented as 1 (black) and -1 (white). 
        Notes on variables:
          - 'playerstones' is a list containing tuples that represent all stones placed by a player.
          - 'directions' represens row-col indices relative to pivot stone in the order of (northwest-southeast), (north-south), (northeast-southwest), and (west-east).
          - 'connected' stores group of connected stone indices at the same index as 'directions'. Ex) [[], [(8, 6), (9, 6)], [], [(7, 7)]] -> nn-ss (three), ww-ee (two) are connected.
          - 'space' variables are integers that represent consecutive spaces within connections. 
          - 'stones' is a list of tuples that stores the group of connected stones in one direction.
          - 'space_allowed' is an integer representing spaces allowed within a connection.
    """
    if debug: print('')

    # gathering player stones
    playerstones = []
    for row in range(len(BoardTracker)):
        for col in range(len(BoardTracker[0])):
            if BoardTracker[row][col] == player: 
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
                if BoardTracker[r+direction[0]*n][c+direction[1]*n] == player: stones.append((r+direction[0]*n, c+direction[1]*n))
                elif (BoardTracker[r+direction[0]*n][c+direction[1]*n] == 0) & (space1 < space_allowed): space1 += 1
                else: break
                
            # "lower" directions
            for n in range(1,7):
                if BoardTracker[r+direction[2]*n][c+direction[3]*n] == player: stones.append((r+direction[2]*n, c+direction[3]*n))
                elif (BoardTracker[r+direction[2]*n][c+direction[3]*n] == 0) & (space2 < space_allowed): space2 += 1
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
    return ones, twos, tres, furs, fivs, sixs, sevs


def IsTerminal(fivs, connect_objective=5):
    """
        If you want to change the termination rule at any case, e.g., if you want to connect 6 rather than connect 5, just change connect_objective=6.
        Here, player is a string--'Black' or 'White'.
    """
    if len(fivs):
        fivs, is_terminal = fivs[0], True
        for s in range(connect_objective-1):
            if (abs(fivs[s][0] - fivs[s+1][0]) < 2) & (abs(fivs[s][1] - fivs[s+1][1]) < 2): continue
            else: is_terminal = False; break
        return is_terminal
    else: return False