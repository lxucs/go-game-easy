from game.go import Board, opponent_color
from agent.util import get_num_endangered_groups, get_liberties
"""
Evaluation functions for search_agent.
"""


def evaluate(board: Board, color):
    if color == board.next:
        return -evaluate(board, opponent_color(color))

    # Score for win or lose
    priority = False  # Normally false because the next move is opponent's, unless opponent is forced to save one of his group.
    winscore = 361. - board.counter_move  # The faster the game is, the more the reward and punishment is.
    if board.winner:
        score_win_lose = winscore if board.winner == color else -winscore
        return score_win_lose

    # Score for endangered groups
    num_endangered_self, num_endangered_oppo = get_num_endangered_groups(board, color)
    if num_endangered_self > 0:
        return -winscore + 1  # Lose in next move
    elif num_endangered_oppo > 1:
        return (winscore - 1) / 1.2  # Large possibility towin
    elif num_endangered_oppo == 1:
        priority = True

    # Score for liberties
    selfscore, opponentscore = get_liberties(board, color)
    if priority:
        finals = opponentscore[0] - selfscore[0] * 0.85 + opponentscore[1] * 0.7 - selfscore[1] * 0.6
    else:
        finals = opponentscore[0] * 0.85 - selfscore[0] + opponentscore[1] * 0.6 - selfscore[1] * 0.7
    return finals * winscore
