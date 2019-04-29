## "Mini" Go Game with AI Agents

An "easier" version of Go game implemented in Python, with more constraints on legal moves, and simpler winning condition.

GUI is provided for human to play; legal actions at each turn are indicated on the board.

Various AI agents are also provided.

Game rules and usage will be edited later.

### Game Rules

This "simplified" version of Go has the same rules and concepts (such as "liberties") as the original Go, with the exceptions on legal actions and winning criteria.

* Legal actions: at each turn, the player can only place the stone on one of opponent's liberties, unless the player has any self-group to save.
    * If there exists any opponent's group that has only one liberty, the legal actions will be these liberties to cause a direct win.
    * Else, if there exists any self-group that has only one liberty, the legal actions will be these liberties to try to save these groups. If sadly there are more than one of these liberties, the player will lose in the next round :(
    * Else, there are no endangered groups for both players; the player should place the stone on one of opponent's liberties.
    * Suicidal moves are not considered as legal actions.

* Winning criteria (one of the following):
    * You remove any opponent's group.
    * There are no legal actions for the opponent (this happens around 1.6% for random plays).

### Usage

#### Start A Match



### Code

match: the full environment to play a match; a match can be started with or without GUI.  
benchmark: the tool to test the performance (e.g. win rate) of AI agents.

game.go: the full backend of this Go game, with all logic needed in the game.  
game.ui: the game GUI on top of the backend.

agent.basic_agent: basic agents including random agent or greedy agent.  
agent.search_agent: agents that utilize searching techniques, including AlphaBeta agent or Expectimax agent.

