from match import Match
from agent.basic_agent import RandomAgent, GreedyAgent
from agent.search_agent import AlphaBetaAgent, ExpectimaxAgent
from agent.rl_agent import ApproxQAgent
from agent.rl_env import RlEnv
from agent.evaluation import evaluate
from statistics import mean


class Benchmark:
    def __init__(self, agent_self, agent_oppo):
        """
        :param agent_self: the agent to evaluate
        :param agent_oppo: the opponent agent, such as RandomAgent, GreedyAgent
        """
        if (agent_self.color == 'BLACK' and agent_oppo.color == 'WHITE') \
                or (agent_self.color == 'WHITE' and agent_oppo.color == 'BLACK'):
            self.agent_self = agent_self
            self.agent_oppo = agent_oppo
        else:
            raise ValueError('Must have one BLACK agent and one WHITE agent!')

    def create_match(self):
        if self.agent_self.color == 'BLACK':
            return Match(agent_black=self.agent_self, agent_white=self.agent_oppo, gui=False)
        else:
            return Match(agent_white=self.agent_self, agent_black=self.agent_oppo, gui=False)

    def run_benchmark(self, num_tests):
        list_win = []
        list_num_moves = []
        list_time_elapsed = []

        for i in range(num_tests):
            print('Running game ' + str(i))
            match = self.create_match()
            match.start()

            list_win.append(match.winner == self.agent_self.color)
            list_num_moves.append(match.counter_move)
            list_time_elapsed.append(match.time_elapsed)

        win_mean = mean(list_win)
        num_moves_mean = mean(list_num_moves)
        time_elapsed_mean = mean(list_time_elapsed)
        return win_mean, num_moves_mean, time_elapsed_mean


if __name__ == '__main__':
    # agent_self = GreedyAgent('BLACK')
    agent_self = AlphaBetaAgent('BLACK', evaluate, 1)
    # agent_self = ExpectimaxAgent('BLACK', evaluate, 2)
    # agent_self = ApproxQAgent('BLACK', RlEnv())
    # agent_self.load('agent/ApproxQAgent_BLACK.npy')

    agent_oppo = RandomAgent('WHITE')
    # agent_oppo = GreedyAgent('WHITE')

    benchmark = Benchmark(agent_self=agent_self, agent_oppo=agent_oppo)
    win_mean, num_moves_mean, time_elapsed_mean = benchmark.run_benchmark(30)
    print('Win rate: %f; Avg # moves: %f; Avg time: %f' % (win_mean, num_moves_mean, time_elapsed_mean))
