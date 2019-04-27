from game.go import Board, opponent_color
from game.ui import UI
import pygame
from agent.ai_agent import RandomAgent


class Arena:
    def __init__(self, agent_black=None, agent_white=None, GUI=True):
        """
        BLACK always has the first move on the center of the board.
        :param agent_black: agent or None(human)
        :param agent_white: agent or None(human)
        :param GUI: if show GUI; always true if there are human agents
        """
        self.agent_black = agent_black
        self.agent_white = agent_white

        GUI = GUI if agent_black and agent_white else True
        self.ui = UI() if GUI else None

        self.board = Board(next_color='BLACK')
        self.winner = None

        self.counter_move = 0
        self.time_elapsed = None

    def start_with_ui(self):
        self.ui.initialize()

        # First move is fixed on the center of board
        first_move = (10, 10)
        self.board.put_stone(first_move, check_legal=False)
        self.ui.draw(first_move, self.board.next)
        self.ui.legal_actions = self.board.get_legal_actions()

        while self.board.winner is not None:
            if self.board.next == 'BLACK':
                point = self.perform_one_move(self.agent_black)
            else:
                point = self.perform_one_move(self.agent_white)

            # Check if action is legal
            if point not in self.ui.legal_actions:
                continue

            # Apply action
            self.board.put_stone(point, check_legal=False)
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
                for action in self.ui.legal_actions:
                    self.ui.draw(action, 'BLUE', 8)

    def perform_one_move(self, agent):
        if agent:
            return self._move_by_agent(agent)
        else:
            return self._move_by_human(agent)

    def _move_by_agent(self, agent):
        return agent.get_action(self.board)

    def _move_by_human(self):
        while True:
            pygame.time.wait(250)
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
                            return stone


if __name__ == '__main__':
    arena = Arena()
    arena.start_with_ui()
