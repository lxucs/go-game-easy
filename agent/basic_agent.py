import random
from game.go import Board, opponent_color
import random


class Agent:
    """Abstract stateless agent."""
    def __init__(self, color):
        """
        :param color: 'BLACK' or 'WHITE'
        """
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
    """Pick the action that kills the liberty of most opponent's groups"""
    def __init__(self, color):
        super().__init__(color)

    def get_action(self, board):
        actions = board.get_legal_actions()
        num_groups = [len(board.libertydict.get_groups(opponent_color(self.color), action)) for action in actions]
        max_num_groups = max(num_groups)
        idx_candidates = [idx for idx, num in enumerate(num_groups) if num == max_num_groups]
        return actions[random.choice(idx_candidates)] if actions else None
