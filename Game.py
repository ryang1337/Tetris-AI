import pygame
import random
import Piece
import Grid

pygame.font.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300
PLAY_HEIGHT = 600
BLOCK_SIZE = 30

TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        pass
        

# returns whether or not the piece is in a valid position
def valid_move(piece, grid):
    formatted = piece.convert_shape_format()
    for pos in formatted:
        if not (0 <= pos[0] < PLAY_WIDTH / BLOCK_SIZE and 0 <= pos[1] < PLAY_HEIGHT / BLOCK_SIZE
                + 3):
            return False
        if pos[1] >= 0:
            if not (grid[pos[1]][pos[0]] == (0, 0, 0)):
                return False
    return True


# returns the change in position for a rotation to be valid and returns a
# tuple with the x and y delta. if there are no possible positions,
# returns a tuple with None and None
def get_possible_rotates(piece, grid, direction):
    kick_delta = (None, None)
    temp = Piece.Piece(piece.x, piece.y, piece.shape)
    temp.rotation = piece.rotation
    if piece.shape == Piece.I:
        if direction == 'left':
            for pos in Piece.I_WALL_KICK_LEFT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y - pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
                    break
        else:
            for pos in Piece.I_WALL_KICK_RIGHT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y - pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
                    break
    else:
        if direction == 'left':
            for pos in Piece.WALL_KICK_LEFT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y - pos[1]
                if valid_move(temp, grid):
                    kick_delta = pos
                    break
        else:
            for pos in Piece.WALL_KICK_RIGHT[temp.rotation]:
                temp.x = piece.x + pos[0]
                temp.y = piece.y - pos[1]
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
    if len(Piece.SHAPE_Q) == 0:
        for s in Piece.SHAPES:
            Piece.SHAPE_Q.append(s)
    shape = random.choice(Piece.SHAPE_Q)
    Piece.SHAPE_Q.remove(shape)
    return Piece.Piece(3, 0, shape)


# draws the lines for the play grid
def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y

    for i in range(1, len(grid)):
        pygame.draw.line(surface, (81, 81, 77), (sx, sy + i * BLOCK_SIZE),
                         (sx + PLAY_WIDTH, sy + i * BLOCK_SIZE))
    for j in range(1, len(grid[0])):
        pygame.draw.line(surface, (81, 81, 77), (sx + j * BLOCK_SIZE, sy),
                         (sx + j * BLOCK_SIZE, sy + PLAY_HEIGHT))


# checks if a row needs to be cleared and moves rows above it down
def clear_rows(grid, locked):
    cleared_below = 0
    for i in range(len(grid) - 1, 0, -1):
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
    sx = (2 * SCREEN_WIDTH - TOP_LEFT_X) / 2 - label_w / 2
    sy = TOP_LEFT_Y
    if piece.shape == Piece.I or piece.shape == Piece.O:
        px = (2 * SCREEN_WIDTH - TOP_LEFT_X) / 2 - 2 * BLOCK_SIZE
    else:
        px = (2 * SCREEN_WIDTH - TOP_LEFT_X) / 2 - 1.5 * BLOCK_SIZE
    py = sy + BLOCK_SIZE + label_h
    formatted = piece.get_piece_format()
    for pair in formatted:
        pygame.draw.rect(surface, piece.color, (px + pair[1] * BLOCK_SIZE,
                                                py + pair[0] * BLOCK_SIZE,
                                                BLOCK_SIZE, BLOCK_SIZE), 0)
    surface.blit(label, (sx, sy))


# draws
def draw_window(surface, grid):
    surface.fill((0, 0, 0))
    pygame.font.init()
    font = pygame.font.SysFont('malgungothicsemilight', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() /
                         2, PLAY_HEIGHT / 25))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j * BLOCK_SIZE,
                                                   TOP_LEFT_Y + (i - 3) *
                                                   BLOCK_SIZE, BLOCK_SIZE,
                                                   BLOCK_SIZE), 0)
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
    sx = TOP_LEFT_X / 2 - label_w / 2
    sy = TOP_LEFT_Y
    if held:
        if piece.shape == Piece.I or piece.shape == Piece.O:
            px = TOP_LEFT_X / 2 - 2 * BLOCK_SIZE
        else:
            px = TOP_LEFT_X / 2 - 1.5 * BLOCK_SIZE
        py = sy + BLOCK_SIZE + label_h
        formatted = piece.get_piece_format()
        for pair in formatted:
            pygame.draw.rect(surface, piece.color, (px + pair[1] * BLOCK_SIZE,
                                                    py + pair[0] * BLOCK_SIZE,
                                                    BLOCK_SIZE, BLOCK_SIZE), 0)
    surface.blit(label, (sx, sy))


def draw_border(surface):
    pygame.draw.rect(surface, (255, 255, 255), (TOP_LEFT_X, TOP_LEFT_Y,
                                                PLAY_WIDTH, PLAY_HEIGHT), 4)


# main game logic
def main(surface):
    locked_positions = {}

    change_piece = False
    run = True

    next_piece = get_shape()
    current_piece = get_shape()

    clock = pygame.time.Clock()

    fall_time = 0
    fall_speed = 0.6

    lock_delay = 0.6
    lock_time = 0
    lock_y = 0
    rotate_count = 0
    is_lock = False

    is_hold = False
    hold_piece = None

    matrix = [[(0, 0, 0) for _ in range(10)] for _ in range(23)]
    play_grid = Grid.Grid(matrix)

    while run:
        play_grid.update_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
        if is_lock:
            lock_time += clock.get_rawtime()
            if current_piece.y > lock_y + 3:
                lock_time = 0
                is_lock = False
                rotate_count = 0

        # timer check for auto dropping
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_move(current_piece, play_grid.grid)) and current_piece.y > -1:
                current_piece.y -= 1
                if is_lock is False:
                    lock_y = current_piece.y
                is_lock = True
                if lock_time / 1000 > lock_delay:
                    if check_lost(current_piece.convert_shape_format()):
                        run = False
                    else:
                        change_piece = True
                    is_lock = False
                    lock_time = 0
                    rotate_count = 0

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
            play_grid.update_grid(locked_positions)
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            clear_rows(play_grid.grid, locked_positions)
            fall_time = 10000
            is_hold = False

        # check keypresses and end game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:  # move left
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not (valid_move(current_piece, play_grid.grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:  # move right
                    current_piece.x += 1
                    if not (valid_move(current_piece, play_grid.grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_z:  # rotate left
                    if is_lock:
                        rotate_count += 1
                    if rotate_count < 10:
                        lock_time = 0
                    current_piece.rotate_left()
                    # check wall kick data
                    delta = get_possible_rotates(current_piece, play_grid.grid, 'left')
                    if delta == (None, None):
                        current_piece.rotate_right()
                    else:
                        current_piece.x += delta[0]
                        current_piece.y -= delta[1]
                if event.key == pygame.K_x:  # rotate right
                    if is_lock:
                        rotate_count += 1
                    if rotate_count < 10:
                        lock_time = 0
                    current_piece.rotate_right()
                    # check wall kick data
                    delta = get_possible_rotates(current_piece, play_grid.grid, 'right')
                    if delta == (None, None):
                        current_piece.rotate_left()
                    else:
                        current_piece.x += delta[0]
                        current_piece.y -= delta[1]
                # hard drop
                if event.key == pygame.K_SPACE:
                    rotate_count = 0
                    lock_time = 0
                    is_lock = False
                    hard_drop(current_piece, play_grid.grid)
                    if not check_lost(current_piece.convert_shape_format()):
                        change_piece = True
                # hold piece
                if event.key == pygame.K_c:
                    # would implement as function but python pass by
                    # reference or whatever it is is weird
                    if not is_hold:
                        rotate_count = 0
                        lock_time = 0
                        is_lock = False
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

        shape_pos = current_piece.convert_shape_format()

        # update grid with current piece position
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            play_grid.grid[y][x] = current_piece.color

        # draw everything
        draw_window(surface, play_grid.grid)
        play_grid.draw_piece_guideline(current_piece, surface, locked_positions)
        draw_border(surface)
        draw_next_shape(next_piece, surface)
        draw_hold_piece(hold_piece, surface, hold_piece is not None)

        # update screen
        pygame.display.update()
    pygame.display.quit()


win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
icon = pygame.image.load('tetris.png')
pygame.display.set_icon(icon)
main(win)