import random
from game.go import Board, opponent_color
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


class AlphaBetaAgent(SearchAgent):
    def __init__(self, color, eval_func, depth):
        super().__init__(color, eval_func, depth)

    def get_action(self, board):
        score, actions = self.max_value(board, 0, float("-inf"), float("inf"))
        return actions[0] if len(actions) > 0 else None

    def max_value(self, board, depth, alpha, beta):
        if self.terminal_test(board) or depth == self.depth:
            return self.eval_func(board, self.color), []

        max_score = float("-inf")
        max_score_actions = None
        for action in board.getLegalActions(0):
            score, actions = self.min_value(state.generateSuccessor(0, action), depth, alpha, beta, 1)
            if score > max_score:
                max_score = score
                max_score_actions = [action] + actions

            if max_score > beta:
                return max_score, max_score_actions

            if max_score > alpha:
                alpha = max_score

        return max_score, max_score_actions

    def min_value(self, board, depth, alpha, beta, agent_index):
        """
        Return (score, actions) pair
        """
        if self.terminal_test(state) or depth == self.depth:
            return self.evaluationFunction(state, self.evaluation_memory), []

        min_score = float("inf")
        min_score_actions = None
        for action in state.getLegalActions(agent_index):
            if agent_index == state.getNumAgents() - 1:  # Last playing of ghosts
                score, actions = self.max_value(state.generateSuccessor(agent_index, action), depth+1, alpha, beta)
            else:  # More playing of ghosts
                score, actions = self.min_value(state.generateSuccessor(agent_index, action), depth, alpha, beta, agent_index+1)
            if score < min_score:
                min_score = score
                min_score_actions = [action] + actions

            if min_score < alpha:
                return min_score, min_score_actions

            if min_score < beta:
                beta = min_score

        return min_score, min_score_actions
