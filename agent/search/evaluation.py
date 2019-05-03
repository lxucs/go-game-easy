from game.go import Board, opponent_color
from agent.util import get_num_endangered_groups, get_liberties, is_dangerous_liberty, get_num_groups_with_k_liberties
from numpy.random import normal
"""
Evaluation functions for search_agent.
"""


def evaluate(board: Board, color):
    """Color has the next action"""
    # Score for win or lose
    score_win = 1000 - board.counter_move  # Prefer faster game
    if board.winner:
        return score_win if board.winner == color else -score_win

    oppo = opponent_color(color)
    # Score for endangered groups
    num_endangered_self, num_endangered_oppo = get_num_endangered_groups(board, color)
    if num_endangered_oppo > 0:
        return score_win - 10  # Win in the next move
    elif num_endangered_self > 1:
        return -(score_win - 10)  # Lose in the next move

    # Score for dangerous liberties
    liberties_self, liberties_oppo = get_liberties(board, color)
    for liberty in liberties_oppo:
        if is_dangerous_liberty(board, liberty, oppo):
            return score_win / 2  # Good probability to win in the next next move
    for liberty in liberties_self:
        if is_dangerous_liberty(board, liberty, color):
            self_groups = board.libertydict.get_groups(color, liberty)
            liberties = self_groups[0].liberties | self_groups[1].liberties
            able_to_save = False
            for lbt in liberties:
                if len(board.libertydict.get_groups(oppo, lbt)) > 0:
                    able_to_save = True
                    break
            if not able_to_save:
                return -score_win / 2  # Good probability to lose in the next next move

    # Score for groups
    num_groups_2lbt_self, num_groups_2lbt_oppo = get_num_groups_with_k_liberties(board, color, 2)
    score_groups = num_groups_2lbt_oppo - num_groups_2lbt_self

    # Score for liberties
    num_shared_liberties_self = 0
    num_shared_liberties_oppo = 0
    for liberty in liberties_self:
        num_shared_liberties_self += len(board.libertydict.get_groups(color, liberty)) - 1
    for liberty in liberties_oppo:
        num_shared_liberties_oppo += len(board.libertydict.get_groups(oppo, liberty)) - 1
    score_liberties = num_shared_liberties_oppo - num_shared_liberties_self

    # Score for groups (doesn't help)
    # score_groups_self = []
    # score_groups_oppo = []
    # for group in board.groups[color]:
        # if group.num_liberty > 1:
            # score_groups_self.append(eval_group(group, board))
    # for group in board.groups[opponent_color(color)]:
        # if group.num_liberty > 1:
            # score_groups_oppo.append(eval_group(group, board))
    # score_groups_self.sort(reverse=True)
    # score_groups_self += [0, 0]
    # score_groups_oppo.sort(reverse=True)
    # score_groups_oppo += [0, 0]
    # finals = score_groups_oppo[0] - score_groups_self[0] + score_groups_oppo[1] - score_groups_self[1]

    return score_groups * normal(1, 0.1) + score_liberties * normal(1, 0.1)
