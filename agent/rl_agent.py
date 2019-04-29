from agent.basic_agent import Agent, RandomAgent
from agent.rl_env import RlEnv
import numpy as np
from game.go import Board
from game.go import opponent_color
import random
from statistics import mean


class RlAgent(Agent):
    def __init__(self, color, rl_env: RlEnv):
        super().__init__(color)
        self.rl_env = rl_env
        self.w = None

    def get_action(self, board):
        raise NotImplementedError


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
            path_file = str(self) + '.npy'
            np.save(path_file, self.w)
            print('Saved weights to ' + path_file)

    def load(self):
        """Load the weight vector."""
        path_file = str(self) + '.npy'
        self.w = np.load(path_file)
        print('Loaded weights from ' + path_file)

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

        exploration_rate_decay = 0.9
        print('Start training ' + str(self))
        for epoch in range(epochs):
            diff_mean = self._train_one_epoch(lr, discount, exploration_rate)
            # Decay exploration_rate
            if epoch % 100 == 99:
                exploration_rate *= exploration_rate_decay
                print('Decay exploration_rate to %f' % exploration_rate)
            # Echo performance
            if epoch % 5 == 4:
                print('Epoch %d: mean difference %f' % (epoch, diff_mean))

    def _train_one_epoch(self, lr, discount, exploration_rate):
        """Return the mean of difference during this epoch"""
        agent_oppo = RandomAgent(opponent_color(self.color))
        board = Board()
        first_move = (10, 10)
        board.put_stone(first_move, check_legal=False)

        if board.next != self.color:
            board.put_stone(agent_oppo.get_action(board), check_legal=False)

        diffs = []
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
            diffs.append(difference)

            # Apply weight update
            self.w += (lr * difference * feats)

        return mean(diffs)

    def _calc_q(self, board, action):
        return self.w.dot(self.rl_env.extract_features(board, action, self.color))


if __name__ == '__main__':
    # Train and save ApproxQAgent
    approx_q_agent = ApproxQAgent('BLACK', RlEnv())
    approx_q_agent.train(5000, 0.1, 0.8, 0.05)
    approx_q_agent.save()
