from game.go import Board, opponent_color
from agent.util import get_num_endangered_groups, get_liberties
import numpy as np
"""
Environment for rl_agent.
"""


class RlEnv:
    def __init__(self):
        pass

    @classmethod
    def get_reward(cls, board: Board, color):
        """Return a scalar reward"""
        if board.winner is None:
            return 0
        return 1000 if board.winner == color else -1000

    @classmethod
    def extract_features(cls, board: Board, action, color):
        """Return a numpy array of features"""
        board_next = board.generate_successor_state(action)

        # Features for win or lose
        feat_win = 1 if board_next.winner == color else 0
        feat_lose = 1 if board_next.winner == opponent_color(color) else 0

        # Feature for groups
        num_groups_self = len(board_next.groups[color])
        num_groups_oppo = len(board_next.groups[opponent_color(color)])
        feat_diff_groups = num_groups_self - num_groups_oppo

        # Features for endangered groups
        num_endangered_self, num_endangered_oppo = get_num_endangered_groups(board_next, color)
        feat_num_endangered_self = num_endangered_self
        feat_num_endangered_oppo = num_endangered_oppo
        feat_diff_endangered = num_endangered_oppo - num_endangered_self

        # Features for liberties
        liberties_self, liberties_oppo = get_liberties(board_next, color)
        feat_diff_liberties = len(liberties_self) - len(liberties_oppo)
        feat_liberties_intersection = len(liberties_self & liberties_oppo)

        feats = [feat_win, feat_lose, feat_diff_groups, feat_num_endangered_self, feat_num_endangered_oppo,
                 feat_diff_endangered, feat_diff_liberties, feat_liberties_intersection, 1]  # Add bias
        return np.array(feats)

    @classmethod
    def get_num_feats(cls):
        board = Board()
        return cls.extract_features(board, (10, 10), 'BLACK').shape[0]
