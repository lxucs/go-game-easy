#!/usr/bin/env python
# coding: utf-8

"""Goban made with Python, pygame and go.py.

This is a front-end for my go library 'go.py', handling drawing and
pygame-related activities. Together they form a fully working goban.

"""

__author__ = "Aku Kotkavuo <aku@hibana.net>"

import pygame
import game.go as go


BACKGROUND = 'images/ramin.jpg'
BOARD_SIZE = (820, 820)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0,0,0)
def transfercolor(color):
    if color=='WHITE':
        return (255, 255, 255)
    elif color=='BLACK':
        return (0, 0, 0)
    else: return (0,133,211)
def coords(point):
    '''coordinate of a stone drawn on board'''
    return (5 + point[0] * 40, 5 + point[1] * 40)

def leftupcorner(point):
    return (-15 + point[0] * 40, -15 + point[1] * 40)


def draw(point,color,size=20):
    color=transfercolor(color)
    """Draw the stone as a circle."""
    pygame.draw.circle(screen, color, coords(point), size, 0)
    pygame.display.update()

def remove(point):
    """Remove the stone from board."""
    blit_coords = leftupcorner(point)
    area_rect = pygame.Rect(blit_coords, (40, 40))
    screen.blit(background, blit_coords, area_rect)
    pygame.display.update()


class Board(go.Board):
    def __init__(self):
        """Create, initialize and draw an empty board."""
        super(Board, self).__init__()
        self.outline = pygame.Rect(45, 45, 720, 720)
        self.draw()

    def draw(self):
        """Draw the board to the background and blit it to the screen.

        The board is drawn by first drawing the outline, then the 19x19
        grid and finally by adding hoshi to the board. All these
        operations are done with pygame's draw functions.

        This method should only be called once, when initializing the
        board.

        """
        pygame.draw.rect(background, BLACK, self.outline, 3)
        # Outline is inflated here for future use as a collidebox for the mouse
        self.outline.inflate_ip(20, 20)
        for i in range(18):
            for j in range(18):
                rect = pygame.Rect(45 + (40 * i), 45 + (40 * j), 40, 40)
                pygame.draw.rect(background, BLACK, rect, 1)
        for i in range(3):
            for j in range(3):
                coords = (165 + (240 * i), 165 + (240 * j))
                pygame.draw.circle(background, BLACK, coords, 5, 0)
        screen.blit(background, (0, 0))
        pygame.display.update()
        
def main(board):
    board.put_stone((10,10))
    draw((10,10),go.opponent_color(board.next))
    legalmove=[]
    legalmoveon=False
    while True:
        pygame.time.wait(250)

        ''''''

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if board.winner:
                    pygame.quit()
                    return board.winner
                if event.button == 1 and board.outline.collidepoint(event.pos):                    
                    x = int(round(((event.pos[0] - 5) / 40.0), 0))
                    y = int(round(((event.pos[1] - 5) / 40.0), 0))
                    point=(x,y)
                    stone = board.exist_stone(point=(x, y))
                    if stone:
                        continue
                    else:
                        if board.put_stone(point,check_legal=True):
                            if legalmoveon:
                                for movement in legalmove:
                                    remove(movement)
                                    legalmoveon=False
                            draw(point,go.opponent_color(board.next))
                            if board.winner:
                                for group in board.removed_groups:
                                    for point in group.points:
                                        remove(point)
                            else:
                                legalmove=board.get_legal_action()
                                if isinstance(legalmove,tuple):
                                    legalmove=[legalmove]
                                else:
                                    legalmove=list(legalmove)
                                #aaa=board.generateSuccessorState(legalmove[0])
                                #aaa.put_stone(aaa.randommove())
                                legalmoveon=True
                                for point in legalmove:
                                    draw(point,BLUE,8)
                                
                                
                print(str(board))


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Goban')
    screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
    background = pygame.image.load(BACKGROUND).convert()
    board = Board()

    main(board)
