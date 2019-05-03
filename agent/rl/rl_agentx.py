from agent.basic_agent import Agent, RandomAgent
from agent.search.search_agent import AlphaBetaAgent
from agent.rl.rl_env import RlEnv2
import numpy as np
from game.go import Board
from game.go import opponent_color
import random
from statistics import mean


class RlAgent(Agent):
    def __init__(self, color, rl_env):
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

    def get_default_path(self):
        return '%s_%s.npy' % (self.__class__.__name__, self.color)

    def save(self, path_file=None):
        """Save the weight vector."""
        if self.w is not None:
            if not path_file:
                path_file = self.get_default_path()
            np.save(path_file, self.w)
            print('Saved weights to ' + path_file)

    def load(self, path_file=None):
        """Load the weight vector."""
        if path_file is None:
            path_file = self.get_default_path()
        self.w = np.load(path_file)
        print('Loaded weights from ' + path_file)

    def train(self, epochs, lr, discount, exploration_rate, decay_rate=0.9, decay_epoch=500):
        """
        Use RandomAgent for opponent.
        :param epochs: one epoch = one game
        :param lr: learning rate
        :param discount:
        :param exploration_rate: the probability to cause self random move during training
        :param decay_rate: the rate to decay learning rate and exploration rate
        :param decay_epoch: the number of epochs to apply decay
        :return:
        """
        if exploration_rate > 1 or exploration_rate < 0:
            raise ValueError('exploration_rate should be in [0, 1]!')

        num_feats = self.rl_env.get_num_feats()
        self.w = np.array([-1]+[-0.5]*(-1+num_feats)+[0.8]+[0.4]*(-1+num_feats))

        print('Start training ' + str(self))
        for epoch in range(epochs):
            diff_mean = self._train_one_epoch(lr, discount, exploration_rate)
            # Decay learning rate and exploration rate
            if epoch % decay_epoch == decay_epoch - 1:
                lr *= decay_rate
                exploration_rate *= decay_rate
                print('Decay learning rate to %f' % lr)
                print('Decay exploration rate to %f' % exploration_rate)
            # Echo performance
            if epoch % 5 == 4:
                print('Epoch %d: mean difference %f' % (epoch, diff_mean))
        print('Finished training')

    def _train_one_epoch(self, lr, discount, exploration_rate):
        """Return the mean of difference during this epoch"""
        # Opponent: minimax with random move
        prob_oppo_random = 0.1
        agent_oppo = AlphaBetaAgent(opponent_color(self.color), depth=1)
        agent_oppo_random = RandomAgent(opponent_color(self.color))

        board = Board()
        first_move = (10, 10)
        board.put_stone(first_move, check_legal=False)

        if board.next != self.color:
            board.put_stone(agent_oppo_random.get_action(board), check_legal=False)

        diffs = []
        while board.winner is None:
            legal_actions = board.get_legal_actions()
            # Get next action with exploration
            if random.uniform(0, 1) < exploration_rate:
                action_next = random.choice(legal_actions)
            else:
                action_next = max(legal_actions, key=lambda action: self._calc_q(board, action))

            # Keep current features
            feats ,isself = self.rl_env.extract_features(board, action_next, self.color)
            if isself:
                q=self.w.dot(feats)
            else:
                q=-self.w.dot(self.rl_env.reverse_features(feats))

            # Apply next action
            board.put_stone(action_next, check_legal=False)
            # Let opponent play
            if board.winner is None:
                if random.uniform(0, 1) < prob_oppo_random:
                    board.put_stone(agent_oppo_random.get_action(board), check_legal=False)
                else:
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
            if isself:
                self.w += (lr * difference * feats)
            else:
                self.w -= (lr * difference * self.rl_env.reverse_features(feats))

        return mean(diffs)

    def _calc_q(self, board, action):
        feats,isself = self.rl_env.extract_features(board, action, self.color)
        if isself:
            return  self.w.dot(feats)
        else:
            return  -self.w.dot(self.rl_env.reverse_features(feats))


if __name__ == '__main__':
    # Train and save ApproxQAgent
    approx_q_agent = ApproxQAgent('BLACK', RlEnv2())
    approx_q_agent.train(2000, 0.001, 0.9, 0.1)
    approx_q_agent.save()
