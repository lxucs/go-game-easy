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
    return score
