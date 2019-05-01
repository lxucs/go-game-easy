#!/usr/bin/env python
from game.go import Board, opponent_color
from game.ui import UI
import pygame
import time
from agent.basic_agent import RandomAgent, GreedyAgent
from agent.search.search_agent import AlphaBetaAgent, ExpectimaxAgent
from agent.rl.rl_agent import ApproxQAgent
from agent.rl.rl_env import RlEnv
from os.path import join
from argparse import ArgumentParser


class Match:
    def __init__(self, agent_black=None, agent_white=None, gui=True, dir_save=None):
        """
        BLACK always has the first move on the center of the board.
        :param agent_black: agent or None(human)
        :param agent_white: agent or None(human)
        :param gui: if show GUI; always true if there are human playing
        :param dir_save: directory to save board image if GUI is shown; no save for None
        """
        self.agent_black = agent_black
        self.agent_white = agent_white

        self.board = Board(next_color='BLACK')

        gui = gui if agent_black and agent_white else True
        self.ui = UI() if gui else None
        self.dir_save = dir_save

        # Metadata
        self.time_elapsed = None

    @property
    def winner(self):
        return self.board.winner

    @property
    def next(self):
        return self.board.next

    @property
    def counter_move(self):
        return self.board.counter_move

    def start(self):
        if self.ui:
            self._start_with_ui()
        else:
            self._start_without_ui()

    def _start_with_ui(self):
        """Start the game with GUI."""
        self.ui.initialize()
        self.time_elapsed = time.time()

        # First move is fixed on the center of board
        first_move = (10, 10)
        self.board.put_stone(first_move, check_legal=False)
        self.ui.draw(first_move, opponent_color(self.board.next))

        # Take turns to play move
        while self.board.winner is None:
            if self.board.next == 'BLACK':
                point = self.perform_one_move(self.agent_black)
            else:
                point = self.perform_one_move(self.agent_white)

            # Check if action is legal
            if point not in self.board.legal_actions:
                continue

            # Apply action
            prev_legal_actions = self.board.legal_actions.copy()
            self.board.put_stone(point, check_legal=False)
            # Remove previous legal actions on board
            for action in prev_legal_actions:
                self.ui.remove(action)
            # Draw new point
            self.ui.draw(point, opponent_color(self.board.next))
            # Update new legal actions and any removed groups
            if self.board.winner:
                for group in self.board.removed_groups:
                    for point in group.points:
                        self.ui.remove(point)
                if self.board.end_by_no_legal_actions:
                    print('Game ends early (no legal action is available for %s)' % self.board.next)
            else:
                for action in self.board.legal_actions:
                    self.ui.draw(action, 'BLUE', 8)

        self.time_elapsed = time.time() - self.time_elapsed
        if self.dir_save:
            path_file = join(self.dir_save, 'go_' + str(time.time()) + '.jpg')
            self.ui.save_image(path_file)
            print('Board image saved in file ' + path_file)

    def _start_without_ui(self):
        """Start the game without GUI. Only possible when no human is playing."""
        # First move is fixed on the center of board
        self.time_elapsed = time.time()
        first_move = (10, 10)
        self.board.put_stone(first_move, check_legal=False)

        # Take turns to play move
        while self.board.winner is None:
            if self.board.next == 'BLACK':
                point = self.perform_one_move(self.agent_black)
            else:
                point = self.perform_one_move(self.agent_white)

            # Apply action
            self.board.put_stone(point, check_legal=False)  # Assuming agent always gives legal actions

        if self.board.end_by_no_legal_actions:
            print('Game ends early (no legal action is available for %s)' % self.board.next)

        self.time_elapsed = time.time() - self.time_elapsed

    def perform_one_move(self, agent):
        if agent:
            return self._move_by_agent(agent)
        else:
            return self._move_by_human()

    def _move_by_agent(self, agent):
        if self.ui:
            pygame.time.wait(100)
            pygame.event.get()
        return agent.get_action(self.board)

    def _move_by_human(self):
        while True:
            pygame.time.wait(100)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.ui.outline.collidepoint(event.pos):
                        x = int(round(((event.pos[0] - 5) / 40.0), 0))
                        y = int(round(((event.pos[1] - 5) / 40.0), 0))
                        point = (x, y)
                        stone = self.board.exist_stone(point)
                        if not stone:
                            return point


def get_args():
    parser = ArgumentParser('Mini Go Game')
    parser.add_argument('-b', '--agent_black', default=None,
                        help='possible agents for BLACK: random; greedy; minimax; expectimax; DEFAULT is None (human)')
    parser.add_argument('-w', '--agent_white', default=None,
                        help='possible agents for WHITE: random; greedy; minimax; expectimax; DEFAULT is None (human)')
    parser.add_argument('-d', '--search_depth', type=int, default=1,
                        help='the search depth for searching agents if applicable; DEFAULT is 1')
    parser.add_argument('-g', '--gui', type=bool, default=True,
                        help='if show GUI; always true if human plays; DEFAULT is True')
    parser.add_argument('-s', '--dir_save', default=None,
                        help='if not None, save the image of last board state to this directory; DEFAULT is None')
    return parser.parse_args()


def get_agent(str_agent, color, depth):
    if str_agent is None:
        return None
    str_agent = str_agent.lower()
    if str_agent == 'none':
        return None
    elif str_agent == 'random':
        return RandomAgent(color)
    elif str_agent == 'greedy':
        return GreedyAgent(color)
    elif str_agent == 'minimax':
        return AlphaBetaAgent(color, depth=depth)
    elif str_agent == 'expectimax':
        return ExpectimaxAgent(color, depth=depth)
    elif str_agent == 'approx-q':
        agent = ApproxQAgent(color, RlEnv())
        agent.load()
        return agent
    else:
        raise ValueError('Invalid agent for ' + color)


def main():
    args = get_args()
    depth = args.search_depth
    agent_black = get_agent(args.agent_black, 'BLACK', depth)
    agent_white = get_agent(args.agent_white, 'WHITE', depth)
    gui = args.gui
    dir_save = args.dir_save

    print('Agent for BLACK: ' + (str(agent_black) if agent_black else 'Human'))
    print('Agent for WHITE: ' + (str(agent_white) if agent_white else 'Human'))
    if dir_save:
        print('Directory to save board image: ' + dir_save)

    match = Match(agent_black=agent_black, agent_white=agent_white, gui=gui, dir_save=dir_save)

    print('Match starts!')
    match.start()

    print(match.winner + ' wins!')
    print('Match ends in ' + str(match.time_elapsed) + ' seconds')
    print('Match ends in ' + str(match.counter_move) + ' moves')


if __name__ == '__main__':
    # match = Match()
    # match = Match(agent_black=RandomAgent('BLACK'))
    # match = Match(agent_black=RandomAgent('BLACK'), agent_white=RandomAgent('WHITE'), gui=True)
    # match = Match(agent_black=RandomAgent('BLACK'), agent_white=RandomAgent('WHITE'), gui=False)
    # match.start()
    # print(match.winner + ' wins!')
    # print('Match ends in ' + str(match.time_elapsed) + ' seconds')
    # print('Match ends in ' + str(match.counter_move) + ' moves')
    main()
