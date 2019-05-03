from agent.basic_agent import Agent
import random
from agent.search.evaluation import evaluate


class SearchAgent(Agent):
    def __init__(self, color, depth, eval_func):
        """
        :param color:
        :param depth: search depth
        :param eval_func: evaluation function from the evaluation module
        """
        super().__init__(color)
        self.depth = depth
        self.eval_func = eval_func
        self.pruning_actions = None

    def get_action(self, board):
        raise NotImplementedError

    def __str__(self):
        return '%s; color: %s; search_depth: %d' % (self.__class__.__name__, self.color, self.depth)


class AlphaBetaAgent(SearchAgent):
    def __init__(self, color, depth, eval_func=evaluate):
        super().__init__(color, depth, eval_func)

    def get_action(self, board, pruning_actions=20):

        self.pruning_actions = pruning_actions
        score, actions = self.max_value(board, 0, float("-inf"), float("inf"))

        return actions[0] if len(actions) > 0 else None

    def max_value(self, board, depth, alpha, beta):
        """Return the highest score and the corresponding subsequent actions"""
        if self.terminal_test(board) or depth == self.depth:
            return self.eval_func(board, self.color), []

        max_score = float("-inf")
        max_score_actions = None
        # Prune the legal actions
        legal_actions = board.get_legal_actions()
        if self.pruning_actions and len(legal_actions) > self.pruning_actions:
            legal_actions = random.sample(legal_actions, self.pruning_actions)

        for action in legal_actions:
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
        # Prune the legal actions
        legal_actions = board.get_legal_actions()
        if self.pruning_actions and len(legal_actions) > self.pruning_actions:
            legal_actions = random.sample(legal_actions, self.pruning_actions)

        for action in legal_actions:
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
    """Assume uniform distribution for opponent"""
    def __init__(self, color, depth, eval_func=evaluate):
        super().__init__(color, depth, eval_func)

    def get_action(self, board, pruning_actions=16):
        self.pruning_actions = pruning_actions
        score, actions = self.max_value(board, 0)
        return actions[0] if len(actions) > 0 else None

    def max_value(self, board, depth):
        if self.terminal_test(board) or depth == self.depth:
            return self.eval_func(board, self.color), []

        max_score = float("-inf")
        max_score_actions = None
        # Prune the legal actions
        legal_actions = board.get_legal_actions()
        if self.pruning_actions and len(legal_actions) > self.pruning_actions:
            legal_actions = random.sample(legal_actions, self.pruning_actions)

        for action in legal_actions:
            score, actions = self.expected_value(board.generate_successor_state(action), depth)
            if score > max_score:
                max_score = score
                max_score_actions = [action] + actions

        return max_score, max_score_actions

    def expected_value(self, board, depth):
        if self.terminal_test(board) or depth == self.depth:
            return self.eval_func(board, self.color), []

        expected_score = 0.0
        # Prune the legal actions
        legal_actions = board.get_legal_actions()
        if self.pruning_actions and len(legal_actions) > self.pruning_actions:
            legal_actions = random.sample(legal_actions, self.pruning_actions)

        for action in legal_actions:
            score, actions = self.max_value(board.generate_successor_state(action), depth+1)
            expected_score += score / len(legal_actions)

        return expected_score, []
