from game.go import Board, opponent_color
from game.ui import UI
import pygame
import time
from agent.ai_agent import RandomAgent
from os.path import join


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
        self.counter_move = 0
        self.time_elapsed = time.time()

    @property
    def winner(self):
        return self.board.winner

    @property
    def next(self):
        return self.board.next

    @property
    def legal_actions(self):
        return self.ui.legal_actions

    def start_with_ui(self):
        """Start the game with UI."""
        self.ui.initialize()

        # First move is fixed on the center of board
        first_move = (10, 10)
        self.board.put_stone(first_move, check_legal=False)
        self.ui.draw(first_move, opponent_color(self.board.next))
        self.ui.legal_actions = self.board.get_legal_actions()

        # Take turns to play move
        while self.board.winner is None:
            if self.board.next == 'BLACK':
                point = self.perform_one_move(self.agent_black)
            else:
                point = self.perform_one_move(self.agent_white)

            # Check if action is legal
            if point not in self.ui.legal_actions:
                continue

            # Apply action
            self.board.put_stone(point, check_legal=False)
            self.counter_move += 1
            # Remove previous legal actions on board
            for action in self.ui.legal_actions:
                self.ui.remove(action)
            # Draw new point
            self.ui.draw(point, opponent_color(self.board.next))
            # Update legal actions and removed groups
            if self.board.winner:
                for group in self.board.removed_groups:
                    for point in group.points:
                        self.ui.remove(point)
                self.ui.legal_actions = []
            else:
                self.ui.legal_actions = self.board.get_legal_actions()
                if len(self.ui.legal_actions) == 0:
                    self.board.winner = opponent_color(self.board.next)
                    print('Game ends early (no legal action is available for %s)' % self.board.next)
                for action in self.ui.legal_actions:
                    self.ui.draw(action, 'BLUE', 8)

        self.time_elapsed = time.time() - self.time_elapsed
        if self.dir_save:
            path_file = join(self.dir_save, 'go_' + str(time.time()) + '.jpg')
            self.ui.save_image(path_file)
            print('Board image saved in file ' + path_file)

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


if __name__ == '__main__':
    # match = Match()
    # match = Match(agent_black=RandomAgent('BLACK'))
    # match = Match(agent_black=RandomAgent('BLACK'), agent_white=RandomAgent('WHITE'), gui=True)
    match = Match(agent_black=RandomAgent('BLACK'), agent_white=RandomAgent('WHITE'), gui=True,
                  dir_save='/Users/liyanxu/Desktop')
    match.start_with_ui()
    print(match.winner + ' wins!')
    print('Match ends in ' + str(match.time_elapsed) + ' s')
