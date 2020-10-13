import pygame
from pygame import gfxdraw
import random
import copy

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
SHAPE_COLORS = [(206, 221, 226), (126, 164, 179), (255, 179, 71),
                (253, 253, 150), (119, 221, 119), (177, 156, 217),
                (255, 105, 97)]


# index 0 - 6 represent shape


# class for Tetrominoes
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


# draws the colors for each square in the grid depending on the locked positions
def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(23)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                color = locked_pos[(j, i)]
                grid[i][j] = color
    return grid


# returns the list of positions of each mino in the tetromino relative to itself
# after calculating the rotation
def get_piece_format(piece):
    f = copy.deepcopy(piece.shape)
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
        if not (0 <= pos[0] < play_width / block_size and 0 <= pos[1] <
                play_height / block_size + 3):
            return False
        if pos[1] >= 0:
            if not (grid[pos[1]][pos[0]] == (0, 0, 0)):
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
                    break
        else:
            for pos in I_WALL_KICK_RIGHT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y + pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
                    break
    else:
        if direction == 'left':
            for pos in WALL_KICK_LEFT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y + pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
                    break
        else:
            for pos in WALL_KICK_RIGHT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y + pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
                    break
    return kick_delta


# checks whether or not the player has lost
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y >= 3:
            return False
    return True


# returns a Piece object using the Random Generator algorithm
# (7-piece bag)
def get_shape():
    if len(SHAPE_Q) == 0:
        for s in SHAPES:
            SHAPE_Q.append(s)
    shape = random.choice(SHAPE_Q)
    SHAPE_Q.remove(shape)
    return Piece(3, 0, shape)


# draws the lines for the play grid
def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(1, len(grid)):
        pygame.draw.line(surface, (81, 81, 77), (sx, sy + i * block_size),
                         (sx + play_width, sy + i * block_size))
    for j in range(1, len(grid[0])):
        pygame.draw.line(surface, (81, 81, 77), (sx + j * block_size, sy),
                         (sx + j * block_size, sy + play_height))


# checks if a row needs to be cleared and moves rows above it down
def clear_rows(grid, locked):
    cleared_below = 0
    for i in range(len(grid) - 1, 2, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            cleared_below += 1
            for j in range(len(row)):
                del locked[(j, i)]
        else:
            for j in range(len(row)):
                if not (grid[i][j] == (0, 0, 0)):
                    locked[(j, i + cleared_below)] = locked[(j, i)]
                    if cleared_below > 0:
                        del locked[(j, i)]


# draws the shape in the 'next' area
def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('malgungothicsemilight', 30)
    label = font.render('Next', 1, (255, 255, 255))
    label_w, label_h = font.size('Next')
    sx = (2 * s_width - top_left_x) / 2 - label_w / 2
    sy = top_left_y
    if piece.shape == I or piece.shape == O:
        px = (2 * s_width - top_left_x) / 2 - 2 * block_size
    else:
        px = (2 * s_width - top_left_x) / 2 - 1.5 * block_size
    py = sy + block_size + label_h
    formatted = get_piece_format(piece)
    for pair in formatted:
        pygame.draw.rect(surface, piece.color, (px + pair[1] * block_size,
                                                py + pair[0] * block_size,
                                                block_size, block_size), 0)
    surface.blit(label, (sx, sy))


# draws
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
                                                   top_left_y + (i - 3) *
                                                   block_size, block_size,
                                                   block_size), 0)
    draw_grid(surface, grid)


# returns True if a key is currently pressed, otherwise False
def key_pressed(input_key):
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[input_key]:
        return True
    else:
        return False


# implementation of hard drop feature
def hard_drop(piece, grid):
    piece.y += 1
    while valid_move(piece, grid):
        piece.y += 1
    piece.y -= 1


# draws the piece in the 'hold' sections
def draw_hold_piece(piece, surface, held):
    font = pygame.font.SysFont('malgungothicsemilight', 30)
    label = font.render('Hold', 1, (255, 255, 255))
    label_w, label_h = font.size('Hold')
    sx = top_left_x / 2 - label_w / 2
    sy = top_left_y
    if held:
        if piece.shape == I or piece.shape == O:
            px = top_left_x / 2 - 2 * block_size
        else:
            px = top_left_x / 2 - 1.5 * block_size
        py = sy + block_size + label_h
        formatted = get_piece_format(piece)
        for pair in formatted:
            pygame.draw.rect(surface, piece.color, (px + pair[1] * block_size,
                                                    py + pair[0] * block_size,
                                                    block_size, block_size), 0)
    surface.blit(label, (sx, sy))


def is_valid_locked(piece, locked):
    formatted = convert_shape_format(piece)
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


# draws a ghost piece that shows where the piece would fall if hard dropped
def draw_piece_guideline(piece, surface, grid, locked):
    temp = Piece(piece.x, piece.y, piece.shape)
    temp.rotation = piece.rotation
    temp.y = move_to_lowest(temp, locked)
    formatted = convert_shape_format(temp)
    for pair in formatted:
        if grid[pair[1]][pair[0]] == (0, 0, 0):
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


def draw_border(surface):
    pygame.draw.rect(surface, (255, 255, 255), (top_left_x, top_left_y,
                                                play_width, play_height), 4)


# main game logic
def main(surface):
    locked_positions = {}

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    rotate_count = 0
    fall_time = 0
    fall_speed = 0.6
    lock_delay = 0.6
    lock_time = 0
    is_hold = False
    hold_piece = None
    is_lock = False
    lock_y = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
        if is_lock:
            lock_time += clock.get_rawtime()
            if current_piece.y > lock_y + 3:
                lock_time = 0
                is_lock = False

        # timer check for auto dropping
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_move(current_piece, grid)) and current_piece.y > -1:
                current_piece.y -= 1
                if is_lock is False:
                    lock_y = current_piece.y
                is_lock = True
                if lock_time / 1000 > lock_delay:
                    if check_lost(convert_shape_format(current_piece)):
                        run = False
                    else:
                        change_piece = True
                    is_lock = False
                    lock_time = 0

        # if down key is pressed, just speed up auto drop, same as soft drop
        if key_pressed(pygame.K_DOWN):
            fall_speed = 0.03
        else:
            fall_speed = 0.6

        # if we need to change the piece, do so and update the locked positions
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            grid = create_grid(locked_positions)
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            clear_rows(grid, locked_positions)
            fall_time = 10000
            is_hold = False

        # check keypresses and end game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:  # move left
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not (valid_move(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:  # move right
                    current_piece.x += 1
                    if not (valid_move(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_z:  # rotate left
                    rotate_count += 1
                    if rotate_count < 10:
                        lock_time = 0
                    current_piece.rotate_left()
                    # check wall kick data
                    delta = get_possible_rotates(current_piece, grid, 'left')
                    if delta == (None, None):
                        current_piece.rotate_right()
                    else:
                        current_piece.x += delta[0]
                        current_piece.y += delta[1]
                if event.key == pygame.K_x:  # rotate right
                    rotate_count += 1
                    if rotate_count < 10:
                        lock_time = 0
                    current_piece.rotate_right()
                    # check wall kick data
                    delta = get_possible_rotates(current_piece, grid, 'right')
                    if delta == (None, None):
                        current_piece.rotate_left()
                    else:
                        current_piece.x += delta[0]
                        current_piece.y += delta[1]
                # hard drop
                if event.key == pygame.K_SPACE:
                    hard_drop(current_piece, grid)
                    if not check_lost(convert_shape_format(current_piece)):
                        change_piece = True
                # hold piece
                if event.key == pygame.K_c:
                    # would implement as function but python pass by
                    # reference or whatever it is is weird
                    if not is_hold:
                        if hold_piece is None:
                            hold_piece = current_piece
                            hold_piece.x = 3
                            hold_piece.y = 0
                            hold_piece.rotation = 0
                            current_piece = next_piece
                            next_piece = get_shape()
                        else:
                            temp = current_piece
                            current_piece = hold_piece
                            hold_piece = temp
                            hold_piece.x = 3
                            hold_piece.y = 0
                            hold_piece.rotation = 0
                        is_hold = True

        shape_pos = convert_shape_format(current_piece)

        # update grid with current piece position
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            grid[y][x] = current_piece.color

        # draw everything
        draw_window(surface, grid)
        draw_piece_guideline(current_piece, surface, grid, locked_positions)
        draw_border(surface)
        draw_next_shape(next_piece, surface)
        draw_hold_piece(hold_piece, surface, hold_piece is not None)

        # update screen
        pygame.display.update()
    pygame.display.quit()


# main menu logic
def main_menu(window):
    main(window)


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
icon = pygame.image.load('tetris.png')
pygame.display.set_icon(icon)
main_menu(win)

# TODO:
# implement non insta lock for soft drop \/
# implement DAS
