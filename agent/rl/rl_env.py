from game.go import Board, opponent_color
from agent.util import get_num_endangered_groups, get_liberties, is_dangerous_liberty, \
    get_num_groups_with_k_liberties, calc_group_liberty_var, get_group_scores, get_liberty_score
import numpy as np
"""
Environment for rl_agent.
"""


class RlEnvBase:
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
        raise NotImplementedError

    @classmethod
    def get_num_feats(cls):
        raise NotImplementedError


class RlEnv(RlEnvBase):
    def __init__(self):
        super().__init__()

    @classmethod
    def extract_features(cls, board: Board, action, color):
        """Return a numpy array of features"""
        board = board.generate_successor_state(action)
        oppo = opponent_color(color)

        # Features for win
        feat_win = 1 if board.winner == color else 0
        if feat_win == 1:
            return np.array([feat_win] + [0] * (cls.get_num_feats() - 1))

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
        var_self, var_oppo = [], []
        for group in board.groups[color]:
            var_self.append(calc_group_liberty_var(group))
        for group in board.groups[oppo]:
            var_oppo.append(calc_group_liberty_var(group))
        feat_var_self_mean = np.mean(var_self)
        feat_var_oppo_mean = np.mean(var_oppo)

        feats = [feat_win, feat_exist_endangered_self, feat_more_than_one_endangered_oppo,
                 feat_exist_guarantee_losing, feat_exist_guarantee_winning, feat_groups_2lbt,
                 feat_shared_liberties, feat_num_groups_diff, feat_var_self_mean,
                 feat_var_oppo_mean, 1]  # Add bias
        return np.array(feats)

    @classmethod
    def get_num_feats(cls):
        return 11


class RlEnv2(RlEnvBase):
    def __init__(self):
        super().__init__()

    @classmethod
    def extract_features(cls, board: Board, action, color, isself=True, generatesuccessor=True):
        
        """Return a numpy array of features"""
        if generatesuccessor:
            board = board.generate_successor_state(action)
        else:
            board.put_stone(action)
        oppo = opponent_color(color)
        
        if board.winner == color:
            return np.array([0] * (cls.get_num_feats()) + [1] + [0] * (cls.get_num_feats() - 1)) , isself
        elif board.winner == oppo:
            return np.array([1] + [0] * (cls.get_num_feats() * 2 - 1)), isself
        
        if color == board.next: # Now opponent's move
            print('fuck! Extract features when color==next!')

        num_endangered_self, num_endangered_oppo = get_num_endangered_groups(board, color)
        
        if num_endangered_self>0:
            return np.array([1] + [0] * (cls.get_num_feats() * 2 - 1)) , isself # Doomed to lose

        elif len(board.legal_actions) == 1: #One choice only
            return cls.extract_features(board, board.legal_actions[0], oppo, not isself, False)
        
        elif num_endangered_oppo>1: 
            return np.array([0] * (cls.get_num_feats()) + [1] + [0] * (cls.get_num_feats() - 1)) , isself # Doomed to win 

        # Features for groups
        num_groups_2lbt_self, num_groups_2lbt_oppo = get_num_groups_with_k_liberties(board, color, 2)

        # Features for number of groups
        num_groups_self = len(board.groups[color])/3.
        num_groups_oppo = len(board.groups[oppo])/3.

        # Features for liberty variance
        self_group_score, oppo_group_score = get_group_scores(board, color)

        feats = [0,num_groups_2lbt_self, num_groups_self] + self_group_score + [0, num_groups_2lbt_oppo ,num_groups_oppo] + oppo_group_score # Add bias
        if len(feats) !=12:
            print('!!!!!!!!!!!!!!!!!!!',len(feats),'@@@@@@@@@@@@@@@@@@@@@')
        return np.array(feats), isself 

    @classmethod
    def get_num_feats(cls):
        return 6
    
    @classmethod
    def reverse_features(cls, feat):
        length=cls.get_num_feats()
        return np.concatenate((feat[length:], feat[:length]))


class RlEnv3(RlEnvBase):
    def __init__(self):
        super().__init__()

    @classmethod
    def extract_features(cls, board: Board, action, color, isself=True, generatesuccessor=True):
        """Return a numpy array of features"""
        if generatesuccessor:
            board = board.generate_successor_state(action)
        else:
            board.put_stone(action)
        oppo = opponent_color(color)
        
        if color == board.next: # Now opponent's move
            print('fuck! Extract features when color==next!')

        num_endangered_self, num_endangered_oppo = get_num_endangered_groups(board, color)
        if num_endangered_self>0:
            return np.array([1] + [0] * (cls.get_num_feats() * 2 - 1)) , isself # Doomed to lose

        elif len(board.legal_actions) == 1: #One choice only
            return cls.extract_features(board, board.legal_actions[0], oppo, not isself, False)
        
        elif num_endangered_oppo>1: 
            return np.array([0] * (cls.get_num_feats() * 2) + [1] + [0] * (cls.get_num_feats() - 1)) , isself # Doomed to win 

        # Features for groups
        num_groups_2lbt_self, num_groups_2lbt_oppo = get_num_groups_with_k_liberties(board, color, 2)

        # Features for number of groups
        num_groups_self = len(board.groups[color])/3.
        num_groups_oppo = len(board.groups[oppo])/3.

        # Features for liberty variance
        self_group_score, oppo_group_score = get_group_scores(board, color)
        
        # Features for liberty score
        self_liberty_scorelist = get_liberty_score(board, color)
        oppo_liberty_scorelist = get_liberty_score(board, oppo)
        feats = [0 , num_groups_2lbt_self, num_groups_self] + self_group_score + self_liberty_scorelist + [0, num_groups_2lbt_oppo ,num_groups_oppo] + oppo_group_score + oppo_liberty_scorelist # Add bias
        if len(feats) !=12:
            print('!!!!!!!!!!!!!!!!!!!',len(feats),'@@@@@@@@@@@@@@@@@@@@@')
        return np.array(feats), isself 

    @classmethod
    def get_num_feats(cls):
        return 9
    
    @classmethod
    def reverse_features(cls, feat):
        length=cls.get_num_feats()
        return np.concatenate((feat[length:], feat[:length]))
