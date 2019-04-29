from agent.basic_agent import Agent, RandomAgent
from agent.rl_env import RlEnv
import numpy as np
from game.go import Board
from game.go import opponent_color


class RlAgent(Agent):
    def __init__(self, color, rl_env: RlEnv):
        super().__init__(color)
        self.rl_env = rl_env
        self.w = None

    def get_action(self, board):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__ + str(hash(self))


class ApproxQAgent(RlAgent):
    def __init__(self, color, rl_env):
        super().__init__(color, rl_env)

    def get_action(self, board):
        if self.w is None:
            raise RuntimeError('Agent hasn\'t been trained!')

        legal_actions = board.get_legal_actions()
        if not legal_actions:
            return None

        return max(legal_actions, key=lambda action: self._calc_q(board, action))

    def save(self):
        if self.w is not None:
            np.save(self.__class__.__name__, self.w)

    def load(self):
        self.w = np.load(self.__class__.__name__ + '.npy')

    def train(self, epochs, lr, time_decay):
        """
        Use RandomAgent for opponent.
        :param epochs: one epoch = one game
        :param lr: learning rate
        :param time_decay:
        :return:
        """
        num_feats = self.rl_env.get_num_feats()
        self.w = np.random.random(num_feats)

        for epoch in range(epochs):
            self._train_one_epoch(lr, time_decay)

    def _train_one_epoch(self, lr, time_decay):
        agent_oppo = RandomAgent(opponent_color(self.color))
        board = Board()
        first_move = (10, 10)
        board.put_stone(first_move, check_legal=False)

        if board.next != self.color:
            board.put_stone(agent_oppo.get_action(board), check_legal=False)

        while board.winner is None:
            if


    def _calc_q(self, board, action):
        return self.w.dot(self.rl_env.extract_features(board, action, self.color))
