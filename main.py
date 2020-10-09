import pygame
import random

pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# SHAPE FORMATS

I = [[1, 0], [1, 1], [1, 2], [1, 3]]

J = [[0, 0], [1, 0], [1, 1], [1, 2]]

L = [[1, 0], [1, 1], [1, 2], [0, 2]]

O = [[0, 1], [0, 2], [1, 1], [1, 2]]

S = [[0, 1], [0, 2], [1, 0], [1, 1]]

T = [[0, 1], [1, 0], [1, 1], [1, 2]]

Z = [[0, 0], [0, 1], [1, 1], [1, 2]]

# wall kick data
I_WALL_KICK_RIGHT = [[(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
                     [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
                     [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
                     [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)]]
I_WALL_KICK_LEFT = [[(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
                    [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
                    [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
                    [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]]
WALL_KICK_RIGHT = [[(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
                   [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
                   [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                   [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]]
WALL_KICK_LEFT = [[(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                  [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
                  [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
                  [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]]

SHAPES = [I, J, L, O, S, T, Z]
SHAPE_Q = [I, J, L, O, S, T, Z]
SHAPE_COLORS = [(206, 221, 226), (255, 179, 71), (126, 164, 179),
                (253, 253, 150), (119, 221, 119), (177, 156, 217),
                (255, 105, 97)]


# index 0 - 6 represent shape


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotate_left(self):
        if self.rotation == 0:
            self.rotation = 3
        else:
            self.rotation -= 1

    def rotate_right(self):
        if self.rotation == 3:
            self.rotation = 0
        else:
            self.rotation += 1


def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                color = locked_pos[(j, i)]
                grid[i][j] = color
    return grid


# returns the list of positions of each mino in the tetromino relative to itself
# after calculating the rotation
def get_piece_format(piece):
    f = piece.shape
    if f != O:
        for i in range(piece.rotation):
            for pair in f:
                temp = pair[0]
                pair[0] = pair[1]
                pair[1] = temp
            if piece.shape == I:
                for pair in f:
                    pair[1] = 3 - pair[1]
            else:
                for pair in f:
                    pair[1] = 2 - pair[1]
    return f


# returns the position of each mino in the tetromino relative to the top left
# corner of the screen
def convert_shape_format(piece):
    piece_format = get_piece_format(piece)
    positions = []
    for pair in piece_format:
        positions.append((piece.x + pair[1], piece.y + pair[0]))

    return positions


# returns whether or not the piece is in a valid position
def valid_move(piece, grid):
    formatted = convert_shape_format(piece)
    for pos in formatted:
        if not (0 <= pos[0] < play_width / block_size and -2 <= pos[1] <
                play_height / block_size):
            return False
        if pos[1] >= 0:
            if not(grid[pos[1]][pos[0]] == (0, 0, 0)):
                return False
    return True


# returns the change in position for a rotation to be valid and returns a tuple
# with the x and y delta. if there are no possible positions, returns a tuple
# with None and None
def get_possible_rotates(piece, grid, direction):
    kick_delta = (None, None)
    temp = Piece(piece.x, piece.y, piece.shape)
    temp.rotation = piece.rotation
    if piece.shape == I:
        if direction == 'left':
            for pos in I_WALL_KICK_LEFT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y + pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
        else:
            for pos in I_WALL_KICK_RIGHT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y + pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
    else:
        if direction == 'left':
            for pos in WALL_KICK_LEFT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y + pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
        else:
            for pos in WALL_KICK_RIGHT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y + pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
    return kick_delta


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    if len(SHAPE_Q) == 0:
        for s in SHAPES:
            SHAPE_Q.append(s)
    shape = random.choice(SHAPE_Q)
    SHAPE_Q.remove(shape)
    return Piece(3, -3, shape)


def draw_text_middle(text, size, color, surface):
    pass


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (81, 81, 77), (sx, sy + i * block_size),
                         (sx + play_width, sy + i * block_size))
    for j in range(len(grid[0])):
        pygame.draw.line(surface, (81, 81, 77), (sx + j * block_size, sy),
                         (sx + j * block_size, sy + play_height))


def clear_rows(grid, locked):
    pass


def draw_next_shape(shape, surface):
    pass


def draw_window(surface, grid):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('malgungothicsemilight', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() /
                         2, play_height / 25))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j * block_size,
                                                   top_left_y + i * block_size,
                                                   block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 255, 255), (top_left_x, top_left_y,
                                                play_width, play_height), 4)
    draw_grid(surface, grid)
    pygame.display.update()


def main(surface):
    locked_positions = {}

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_move(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
                fall_speed = 0.5
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not (valid_move(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not (valid_move(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    fall_speed = 0.13
                if event.key == pygame.K_z:
                    current_piece.rotate_left()
                    delta = get_possible_rotates(current_piece, grid, 'left')
                    if delta == (None, None):
                        current_piece.rotate_right()
                    else:
                        current_piece.x += delta[0]
                        current_piece.y += delta[1]
                if event.key == pygame.K_x:
                    current_piece.rotate_right()
                    delta = get_possible_rotates(current_piece, grid, 'right')
                    if delta == (None, None):
                        current_piece.rotate_left()
                    else:
                        current_piece.x += delta[0]
                        current_piece.y += delta[1]
                if event.key == pygame.K_SPACE:
                    fall_speed = 0.001
            if event == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    fall_speed = 0.5
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

        draw_window(surface, grid)

        if check_lost(locked_positions):
            run = False
    pygame.display.quit()


def main_menu(window):
    main(window)


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
icon = pygame.image.load('tetris.png')
pygame.display.set_icon(icon)
main_menu(win)  # start game

# TODO:
# fix rotation bug
# fix end game bug
# fix soft drop not stopping after releasing key down bug
# fix initial rotation position bug \/
