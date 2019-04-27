from game.go import Board
from agent.ai_agent import RandomAgent


class Arena:
    def __init__(self, agent_black=None, agent_white=None, GUI=True):
        """
        BLACK has the first move.
        :param agent_black: agent or None(human)
        :param agent_white: agent or None(human)
        :param GUI: if show GUI; always true if there are human agents
        """
        self.agent_black = agent_black
        self.agent_white = agent_white
        self.GUI = GUI if agent_black and agent_white else True

        self.next = 'BLACK'
        self.board = Board(next_color=self.next)
        self.winner = None

        self.counter_move = 0
        self.time_elapsed = None

    def start(self):


    def move_by_agent(self):
        pass

    def move_by_human(self):
        pass
