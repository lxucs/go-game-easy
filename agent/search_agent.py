from agent.basic_agent import Agent


class SearchAgent(Agent):
    def __init__(self, color, eval_func, depth):
        """
        :param color:
        :param eval_func: evaluation function from the evaluation module
        :param depth: search depth
        """
        super().__init__(color)
        self.eval_func = eval_func
        self.depth = depth

    def get_action(self, board):
        raise NotImplementedError

    def __str__(self):
        return '%s; color: %s; search_depth: %d' % (self.__class__.__name__, self.color, self.depth)


class AlphaBetaAgent(SearchAgent):
    def __init__(self, color, eval_func, depth):
        super().__init__(color, eval_func, depth)

    def get_action(self, board):
        score, actions = self.max_value(board, 0, float("-inf"), float("inf"))
        return actions[0] if len(actions) > 0 else None

    def max_value(self, board, depth, alpha, beta):
        """Return the highest score and the corresponding subsequent actions"""
        if self.terminal_test(board) or depth == self.depth:
            return self.eval_func(board, self.color), []

        max_score = float("-inf")
        max_score_actions = None
        for action in board.get_legal_actions():
            score, actions = self.min_value(board.generate_successor_state(action), depth, alpha, beta)
            if score > max_score:
                max_score = score
                max_score_actions = [action] + actions

            if max_score > beta:
                return max_score, max_score_actions

            if max_score > alpha:
                alpha = max_score

        return max_score, max_score_actions

    def min_value(self, board, depth, alpha, beta):
        """Return the lowest score and the corresponding subsequent actions"""
        if self.terminal_test(board) or depth == self.depth:
            return self.eval_func(board, self.color), []

        min_score = float("inf")
        min_score_actions = None
        for action in board.get_legal_actions():
            score, actions = self.max_value(board.generate_successor_state(action), depth+1, alpha, beta)
            if score < min_score:
                min_score = score
                min_score_actions = [action] + actions

            if min_score < alpha:
                return min_score, min_score_actions

            if min_score < beta:
                beta = min_score

        return min_score, min_score_actions


class ExpectimaxAgent(SearchAgent):
    def __init__(self, color, eval_func, depth):
        super().__init__(color, eval_func, depth)

    def get_action(self, board):
        score, actions = self.max_value(board, 0)
        return actions[0] if len(actions) > 0 else None

    def max_value(self, board, depth):
        if self.terminal_test(board) or depth == self.depth:
            return self.eval_func(board, self.color), []

        max_score = float("-inf")
        max_score_actions = None
        for action in board.get_legal_actions():
            score, actions = self.expected_value(board.generate_successor_state(action), depth)
            if score > max_score:
                max_score = score
                max_score_actions = [action] + actions

        return max_score, max_score_actions

    def expected_value(self, board, depth):
        if self.terminal_test(board) or depth == self.depth:
            return self.eval_func(board, self.color), []

        expected_score = 0.0
        legal_actions = board.get_legal_actions()
        for action in legal_actions:
            score, actions = self.max_value(board.generate_successor_state(action), depth+1)
            expected_score += score / len(legal_actions)

        return expected_score, []