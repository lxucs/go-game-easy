from game.go import Board, opponent_color
from agent.util import get_num_endangered_groups, get_liberties, is_dangerous_liberty, get_num_groups_with_k_liberties, calc_group_liberty_var
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
        return 10 if board.winner == color else -10

    @classmethod
    def extract_features(cls, board: Board, action, color):
        """Return a numpy array of features"""
        board = board.generate_successor_state(action)
        oppo = opponent_color(color)

        # Features for win
        feat_win = 1 if board.winner == color else 0

        # Features for endangered groups
        num_endangered_self, num_endangered_oppo = get_num_endangered_groups(board, color)
        feat_exist_endangered_self = 1 if num_endangered_self > 0 else 0
        feat_more_than_one_endangered_oppo = 1 if num_endangered_oppo > 1 else 0

        # Features for dangerous liberties
        feat_exist_guarantee_losing = 0
        feat_exist_guarantee_winning = 0
        liberties_self, liberties_oppo = get_liberties(board, color)
        for liberty in liberties_self:
            if is_dangerous_liberty(board, liberty, color):
                feat_exist_guarantee_losing = 1
                break
        for liberty in liberties_oppo:
            if is_dangerous_liberty(board, liberty, oppo):
                oppo_groups = board.libertydict.get_groups(oppo, liberty)
                liberties = oppo_groups[0].liberties | oppo_groups[1].liberties
                able_to_save = False
                for lbt in liberties:
                    if len(board.libertydict.get_groups(color, lbt)) > 0:
                        able_to_save = True
                        break
                if not able_to_save:
                    feat_exist_guarantee_winning = 1
                    break

        # Features for groups
        num_groups_2lbt_self, num_groups_2lbt_oppo = get_num_groups_with_k_liberties(board, color, 2)
        feat_groups_2lbt = num_groups_2lbt_oppo - num_groups_2lbt_self

        # Features for shared liberties
        num_shared_liberties_self = 0
        num_shared_liberties_oppo = 0
        for liberty in liberties_self:
            num_shared_liberties_self += len(board.libertydict.get_groups(color, liberty)) - 1
        for liberty in liberties_oppo:
            num_shared_liberties_oppo += len(board.libertydict.get_groups(oppo, liberty)) - 1
        feat_shared_liberties = num_shared_liberties_oppo - num_shared_liberties_self

        # Features for number of groups
        feat_num_groups_diff = len(board.groups[color]) - len(board.groups[oppo])

        # Features for liberty variance
        var_x_self, var_y_self = [], []
        var_x_oppo, var_y_oppo = [], []
        for group in board.groups[color]:
            var_x, var_y = calc_group_liberty_var(group)
            var_x_self.append(var_x)
            var_y_self.append(var_y)
        for group in board.groups[oppo]:
            var_x, var_y = calc_group_liberty_var(group)
            var_x_oppo.append(var_x)
            var_y_oppo.append(var_y)
        feat_var_x_self_mean = np.mean(var_x_self)
        feat_var_y_self_mean = np.mean(var_y_self)
        feat_var_x_oppo_mean = np.mean(var_x_oppo)
        feat_var_y_oppo_mean = np.mean(var_y_oppo)

        feats = [feat_win, feat_exist_endangered_self, feat_more_than_one_endangered_oppo,
                 feat_exist_guarantee_losing, feat_exist_guarantee_winning, feat_groups_2lbt,
                 feat_shared_liberties, feat_num_groups_diff, feat_var_x_self_mean,
                 feat_var_y_self_mean, feat_var_x_oppo_mean, feat_var_y_oppo_mean, 1]  # Add bias
        return np.array(feats)

    @classmethod
    def get_num_feats(cls):
        board = Board()
        return cls.extract_features(board, (10, 10), 'BLACK').shape[0]
