from agent.basic_agent import Agent, RandomAgent
from agent.rl_env import RlEnv
import numpy as np
from game.go import Board
from game.go import opponent_color
import random


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
            raise RuntimeError('Agent needs to be trained or loaded!')

        legal_actions = board.get_legal_actions()
        if not legal_actions:
            return None

        return max(legal_actions, key=lambda action: self._calc_q(board, action))

    def save(self):
        """Save the weight vector."""
        if self.w is not None:
            np.save(self.__class__.__name__, self.w)

    def load(self):
        """Load the weight vector."""
        self.w = np.load(self.__class__.__name__ + '.npy')

    def train(self, epochs, lr, discount, exploration_rate):
        """
        Use RandomAgent for opponent.
        :param epochs: one epoch = one game
        :param lr: learning rate
        :param discount:
        :param exploration_rate: the probability to cause random move during training
        :return:
        """
        if exploration_rate > 1 or exploration_rate < 0:
            raise ValueError('exploration_rate should be in [0, 1]!')

        num_feats = self.rl_env.get_num_feats()
        self.w = np.random.random(num_feats)

        for epoch in range(epochs):
            self._train_one_epoch(lr, discount, exploration_rate)

    def _train_one_epoch(self, lr, discount, exploration_rate):
        agent_oppo = RandomAgent(opponent_color(self.color))
        board = Board()
        first_move = (10, 10)
        board.put_stone(first_move, check_legal=False)

        if board.next != self.color:
            board.put_stone(agent_oppo.get_action(board), check_legal=False)

        while board.winner is None:
            legal_actions = board.get_legal_actions()

            # Get next action with exploration
            if random.uniform(0, 1) < exploration_rate:
                action_next = random.choice(legal_actions)
            else:
                action_next = max(legal_actions, key=lambda action: self._calc_q(board, action))

            # Keep current features
            feats = self.rl_env.extract_features(board, action_next, self.color)
            q = self.w.dot(feats)

            # Apply next action
            board.put_stone(action_next, check_legal=False)

            # Let opponent play
            if board.winner is None:
                board.put_stone(agent_oppo.get_action(board), check_legal=False)

            # Calc difference
            reward_now = self.rl_env.get_reward(board, self.color)
            reward_future = 0
            if board.winner is None:
                next_legal_actions = board.get_legal_actions()
                next_qs = [self._calc_q(board, action) for action in next_legal_actions]
                reward_future = max(next_qs)
            difference = reward_now + discount * reward_future - q

            # Apply weight update
            self.w += (lr * difference * feats)

    def _calc_q(self, board, action):
        return self.w.dot(self.rl_env.extract_features(board, action, self.color))
