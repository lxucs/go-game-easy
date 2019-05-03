from game.go import Board, opponent_color, Group
import numpy as np


def get_num_endangered_groups(board: Board, color):
    num_endangered_self = 0
    num_endangered_oppo = 0
    for group in board.endangered_groups:
        if group.color == color:
            num_endangered_self += 1
        else:
            num_endangered_oppo += 1
    return num_endangered_self, num_endangered_oppo


def get_num_groups_with_k_liberties(board: Board, color, k):
    num_groups_self = 0
    num_groups_oppo = 0
    for group in board.groups[color]:
        if group.num_liberty == k:
            num_groups_self += 1
    for group in board.groups[opponent_color(color)]:
        if group.num_liberty == k:
            num_groups_oppo += 1
    return num_groups_self, num_groups_oppo


def get_liberties(board: Board, color):
    liberties_self = set()
    liberties_oppo = set()
    for group in board.groups[color]:
        liberties_self = liberties_self | group.liberties
    for group in board.groups[opponent_color(color)]:
        liberties_oppo = liberties_oppo | group.liberties
    return liberties_self, liberties_oppo


def is_dangerous_liberty(board: Board, point, color):
    self_groups = board.libertydict.get_groups(color, point)
    return len(self_groups) == 2 and self_groups[0].num_liberty == 2 and self_groups[1].num_liberty == 2


def calc_group_liberty_var(group: Group):
    var_x = np.var([x[0] for x in group.liberties])
    var_y = np.var([x[1] for x in group.liberties])
    return var_x + var_y


def eval_group(group: Group, board: Board):
    """Evaluate the liveliness of group; higher score, more endangered"""
    if group.num_liberty > 3:
        return 0
    elif group.num_liberty == 1:
        return 5

    # Till here, group has either 2 or 3 liberties.
    var_x = np.var([x[0] for x in group.liberties])
    var_y = np.var([x[1] for x in group.liberties])
    var_sum = var_x + var_y
    if var_sum < 0.1:
        print('var_sum < 0.1')

    num_shared_liberty = 0
    for liberty in group.liberties:
        num_shared_self_groups = len(board.libertydict.get_groups(group.color, liberty))
        num_shared_oppo_groups = len(board.libertydict.get_groups(opponent_color(group.color), liberty))
        if num_shared_self_groups == 3 and num_shared_oppo_groups == 0:  # Group is safe
            return 0
        elif num_shared_self_groups == 2 or num_shared_self_groups == 3:
            num_shared_liberty += 1

    if num_shared_liberty == 1 and var_sum <= 0.5:
        score = 1/np.sqrt(group.num_liberty)/var_sum/4.
    elif num_shared_liberty == 2 and var_sum > 0.3:
        score = 1/np.sqrt(group.num_liberty)/var_sum/8.
    else:
        score = 1/np.sqrt(group.num_liberty)/var_sum/6.
        if np.sqrt(group.num_liberty)<1.1:
            print('fuck!', group.num_liberty, board.winner)
        if var_sum<0.2:
            print('shit!')
    return score


def get_group_scores(board: Board, color):
    selfscore=[]
    opponentscore=[]
    for group in board.groups[color]:
        if group.num_liberty != 1:
            selfscore.append(eval_group(group, board))
    for group in board.groups[opponent_color(color)]:
        if group.num_liberty != 1:
            opponentscore.append(eval_group(group, board))
    selfscore.sort(reverse=True)
    selfscore.extend([0, 0, 0])
    opponentscore.sort(reverse=True)
    opponentscore.extend([0, 0, 0])
    return selfscore[:3], opponentscore[:3]


def get_liberty_score(board: Board, color):
    scores = []
    share3 = 0
    for liberty, groups in board.libertydict.get_items(color):
        if len(groups) == 0:
            continue
        elif len(groups) == 3:
            share3 += 1
            continue
        else:
            scores.append(sum([0.353 / group.num_liberty / calc_group_liberty_var(group) for group in groups]))
    scores.sort(reverse=True)
    scores.extend([0, 0])
    return scores[:2] + [-share3 / 2.]
