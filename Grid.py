import Piece
import pygame
from pygame import gfxdraw

s_width = 800
s_height = 700
play_width = 300
play_height = 600
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


class Grid(object):
    def __init__(self, grid):
        self.grid = grid

    # updates the colors for each square in the grid depending on the locked positions
    def update_grid(self, locked_pos):
        self.grid = [[(0, 0, 0) for _ in range(10)] for _ in range(23)]

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if (j, i) in locked_pos:
                    color = locked_pos[(j, i)]
                    self.grid[i][j] = color

    # draws a ghost piece that shows where the piece would fall if hard dropped
    def draw_piece_guideline(self, piece, surface, locked):
        temp = Piece.Piece(piece.x, piece.y, piece.shape)
        temp.rotation = piece.rotation
        temp.y = move_to_lowest(temp, locked)
        formatted = temp.convert_shape_format()
        for pair in formatted:
            if self.grid[pair[1]][pair[0]] == (0, 0, 0):
                x = top_left_x + pair[0] * block_size
                y = top_left_y + (pair[1] - 3) * block_size
                w = block_size
                h = block_size
                width = 4
                width = min(min(width, w // 2), h // 2)
                for i in range(width):
                    pygame.gfxdraw.rectangle(surface, (x + i, y + i, w - i * 2 +
                                                       1, h - i * 2 + 1), (81, 81, 77))
                for i in range(width + 4, width + 6):
                    pygame.gfxdraw.rectangle(surface, (x + i, y + i, w - i * 2 +
                                                       1, h - i * 2 + 1), (81, 81, 77))


def is_valid_locked(piece, locked):
    formatted = piece.convert_shape_format()
    for pos in formatted:
        if pos[1] > 22:
            return False
        if pos in locked:
            return False
    return True


def move_to_lowest(piece, locked):
    drop = True
    while drop:
        piece.y += 1
        if not is_valid_locked(piece, locked):
            drop = False
    piece.y -= 1
    return piece.y
