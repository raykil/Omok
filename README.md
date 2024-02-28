# Omok
AI Omok player development.

To start playing game, execute ```python display.py``` in Terminal.

## Scoring Scheme
- Longer the connection is, the higher its corresponding score should be. That is, if a player has a two and a three, three should contribute higher score.
- Total score is normalized to 5. This means that each group of n-connections should have an ultimate limit on how much it can contribute to the score. That means the more n-connection a player has, the less an individual n-connection contributes to the total score. For example, if a player makes a first three, then it would add 3 (or a normalized version of 3), while if a player makes a second three, each three would contribute 1.6 (or its corresponding normalized version), adding up to 3.2 (or normalized). The threshold does not have to be evenly distributed throughout Ns.



### Dependencies
- pygame

To install pygame, visit https://www.pygame.org/download.shtml.