import random


class Agent:
    def __init__(self, color):
        self.color = color

    @classmethod
    def terminal_test(cls, board):
        return board.winner is not None

    def get_action(self, board):
        raise NotImplementedError


class RandomAgent(Agent):
    def __init__(self, color):
        super().__init__(color)

    def get_action(self, board):
        actions = board.get_legal_actions()
        return random.choice(actions) if actions else None


class SearchAgent(Agent):
    def __init__(self, color, eval_func):
        super().__init__(color)
        self.eval_func = eval_func

    def get_action(self, board):
        raise NotImplementedError


class TestSearchAgent(SearchAgent):
    def __init__(self, color, eval_func):
        super().__init__(color, eval_func)

    def get_action(self, board):
        score = self.eval_func(board, self.color)
        actions = board.get_legal_actions()
        return random.choice(actions) if actions else None


if __name__ == '__main__':
    agent = Agent('BLACK')
    agent.get_action(None)
