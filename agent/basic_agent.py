import random
from game.go import Board, opponent_color


class Agent:
    """Abstract stateless agent."""
    def __init__(self, color):
        self.color = color

    @classmethod
    def terminal_test(cls, board):
        return board.winner is not None

    def get_action(self, board: Board):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__ + '; color: ' + self.color


class RandomAgent(Agent):
    """Pick a random action."""
    def __init__(self, color):
        super().__init__(color)

    def get_action(self, board):
        actions = board.get_legal_actions()
        return random.choice(actions) if actions else None


class GreedyAgent(Agent):
    """Pick the action that kills the most liberties of opponent's"""
    def __init__(self, color):
        super().__init__(color)

    def get_action(self, board):
        actions = board.get_legal_actions()
        return max(actions, key=lambda action:
                   len(board.libertydict.get_groups(opponent_color(self.color), action))) if actions else None
