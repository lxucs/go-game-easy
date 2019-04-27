#!/usr/bin/env python
import pygame
import game.go as go

BACKGROUND = 'game/images/ramin.jpg'
BOARD_SIZE = (820, 820)
BLACK = (0, 0, 0)


def get_rbg(color):
    if color == 'WHITE':
        return 255, 255, 255
    elif color == 'BLACK':
        return 0, 0, 0
    else:
        return 0, 133, 211


def coords(point):
    """Return the coordinate of a stone drawn on board"""
    return 5 + point[0] * 40, 5 + point[1] * 40


def leftup_corner(point):
    return -15 + point[0] * 40, -15 + point[1] * 40


class UI:
    def __init__(self):
        """Create, initialize and draw an empty board."""
        self.outline = pygame.Rect(45, 45, 720, 720)
        self.legal_actions = []
        self.screen = None
        self.background = None

    def initialize(self):
        """This method should only be called once, when initializing the board."""
        # This method is from https://github.com/eagleflo/goban/blob/master/goban.py
        pygame.init()
        pygame.display.set_caption('Goban')
        self.screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
        self.background = pygame.image.load(BACKGROUND).convert()

        pygame.draw.rect(self.background, BLACK, self.outline, 3)
        # Outline is inflated here for future use as a collidebox for the mouse
        self.outline.inflate_ip(20, 20)
        for i in range(18):
            for j in range(18):
                rect = pygame.Rect(45 + (40 * i), 45 + (40 * j), 40, 40)
                pygame.draw.rect(self.background, BLACK, rect, 1)
        for i in range(3):
            for j in range(3):
                coords = (165 + (240 * i), 165 + (240 * j))
                pygame.draw.circle(self.background, BLACK, coords, 5, 0)
        self.screen.blit(self.background, (0, 0))
        pygame.display.update()

    def draw(self, point, color, size=20):
        color = get_rbg(color)
        pygame.draw.circle(self.screen, color, coords(point), size, 0)
        pygame.display.update()

    def remove(self, point):
        blit_coords = leftup_corner(point)
        area_rect = pygame.Rect(blit_coords, (40, 40))
        self.screen.blit(self.background, blit_coords, area_rect)
        pygame.display.update()


def main(ui, board):
    board.put_stone((10, 10))
    ui.draw((10, 10), go.opponent_color(board.next))
    while True:
        pygame.time.wait(250)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if board.winner:
                    pygame.quit()
                    return board.winner
                if event.button == 1 and ui.outline.collidepoint(event.pos):
                    x = int(round(((event.pos[0] - 5) / 40.0), 0))
                    y = int(round(((event.pos[1] - 5) / 40.0), 0))
                    point = (x, y)
                    stone = board.exist_stone(point=(x, y))
                    if stone:
                        continue
                    else:
                        if board.put_stone(point, check_legal=True):
                            for action in ui.legal_actions:
                                    ui.remove(action)
                            ui.legal_actions = []
                            ui.draw(point, go.opponent_color(board.next))
                            if board.winner:
                                for group in board.removed_groups:
                                    for point in group.points:
                                        ui.remove(point)
                            else:
                                ui.legal_actions = board.get_legal_actions()
                                for action in ui.legal_actions:
                                    ui.draw(action, 'BLUE', 8)

                print(str(board))


if __name__ == '__main__':
    board = go.Board()
    ui = UI()
    main(ui, board)
