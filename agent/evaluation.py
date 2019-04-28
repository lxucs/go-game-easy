from game.go import Board, opponent_color


def evaluate(board: Board, color):
    # Score for win or lose
    if board.winner:
        score_win_lose = 1000 if board.winner == color else -1000
        score_win_lose -= board.counter_move  # Prefer faster game
        return score_win_lose

    # Score for faster game
    score_num_moves = -board.counter_move

    # Score for endangered groups
    num_endangered_self = 0
    num_endangered_oppo = 0
    for group in board.endangered_groups:
        if group.color == color:
            num_endangered_self += 1
        else:
            num_endangered_oppo += 1
    score_endangered_group = 200 * (num_endangered_oppo - num_endangered_self)

    # Score for liberties
    liberties_self = set()
    liberties_oppo = set()
    for group in board.groups[color]:
        liberties_self = liberties_self | group.liberties
    for group in board.groups[opponent_color(color)]:
        liberties_oppo = liberties_oppo | group.liberties
    score_liberties = 30 * (len(liberties_self) - len(liberties_oppo))

    score_final = score_num_moves + score_endangered_group + score_liberties
    return score_final
