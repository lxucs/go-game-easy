from game.go import Board
from agent.util import get_num_endangered_groups, get_liberties
"""
Evaluation functions for search_agent.
"""


def evaluate(board: Board, color):
    # Score for win or lose
    if board.winner:
        score_win_lose = 1000 if board.winner == color else -1000
        score_win_lose -= board.counter_move  # Prefer faster game
        return score_win_lose

    # Score for faster game
    score_num_moves = -board.counter_move

    # Score for endangered groups
    num_endangered_self, num_endangered_oppo = get_num_endangered_groups(board, color)
    score_endangered_group = 200 * (num_endangered_oppo - num_endangered_self)

    # Score for liberties
    liberties_self, liberties_oppo = get_liberties(board, color)
    score_liberties = 30 * (len(liberties_self) - len(liberties_oppo))

    score_final = score_num_moves + score_endangered_group + score_liberties
    return score_final
