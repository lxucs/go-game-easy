from game.go import Board, opponent_color
from agent.util import get_num_endangered_groups, get_liberties
import numpy as np
"""
Environment for rl_agent.
"""


def get_reward(board: Board, color):
    if board.winner is None:
        return 0
    return 1000 if board.winner == color else -1000


def extract_features(board: Board, action, color):
    board_next = board.generate_successor_state(action)

    # Features for win or lose
    feat_win = 1 if board_next.winner == color else 0
    feat_lose = 1 if board_next.winner == opponent_color(color) else 0

    # Features for endangered groups
    num_endangered_self, num_endangered_oppo = get_num_endangered_groups(board_next, color)
    feat_num_endangered_self = num_endangered_self
    feat_num_endangered_oppo = num_endangered_oppo
    feat_diff_endangered = num_endangered_oppo - num_endangered_self

    # Features for liberties
    liberties_self, liberties_oppo = get_liberties(board, color)
    feat_diff_liberties = len(liberties_self) - len(liberties_oppo)
    feat_liberties_intersection = len(liberties_self & liberties_oppo)




