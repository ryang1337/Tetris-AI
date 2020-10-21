import pygame
import random
import Piece
import Grid


class Game:
    pygame.font.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 700
    PLAY_WIDTH = 300
    PLAY_HEIGHT = 600
    BLOCK_SIZE = 30

    TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
    TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT

    '''
    Vars:
        locked_positions (dict): positions of pieces that are locked in place k: position, v: color
        change_piece (bool): whether or not we need to change the current piece to next piece
        run (bool): if true, we run the game, if false, we don't run the game
        next_piece (Piece): the next piece in the queue
        current_piece (Piece): the current piece we are controlling
        clock (clock): used for intervals and delays
        fall_time (int): how long the current piece has been falling, if > than fall_speed * 
                         1000, move current_piece y position down one square
        fall_speed (int): how long before current_piece moves down one square by itself
        lock_delay (int): how long before piece locks in place after collision with a locked piece
        lock_time (int): duration of time after current_piece collides with locked piece
        lock_y (int): y position of current_piece after collision with locked piece, used to reset 
                      lock_time and rotate_count
        rotate_count (int): how many times the piece has rotated after collision with locked piece
        is_lock (bool): true if piece is in a pre lock state, i.e. after collision but before 
                        being locked
        is_hold (bool): true if there is a hold_piece is not None
        hold_piece (Piece): piece that is being held
        score (int): score of game
        play_grid (Grid): the grid where the game and logic is run
    '''

    def __init__(self):
        self.win = pygame.display.set_mode((Game.SCREEN_WIDTH, Game.SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        icon = pygame.image.load('tetris.png')
        pygame.display.set_icon(icon)

        self.locked_positions = None
        self.change_piece = None
        self.run = None
        self.next_piece = None
        self.current_piece = None

        self.clock = None

        self.fall_time = None
        self.fall_speed = None

        self.lock_delay = None
        self.lock_time = None
        self.lock_y = None
        self.rotate_count = None
        self.is_lock = None

        self.is_hold = None
        self.hold_piece = None

        self.score = None

        self.play_grid = None
        self.reset()

    def reset(self):
        for shape in Piece.SHAPE_Q:
            Piece.SHAPE_Q.remove(shape)
        for s in Piece.SHAPES:
            Piece.SHAPE_Q.append(s)

        self.locked_positions = {}

        self.change_piece = False
        self.run = True

        self.next_piece = self.get_shape()
        self.current_piece = self.get_shape()

        self.clock = pygame.time.Clock()

        self.fall_time = 0
        self.fall_speed = 0.6

        self.lock_delay = 0.6
        self.lock_time = 0
        self.lock_y = 0
        self.rotate_count = 0
        self.is_lock = False

        self.is_hold = False
        self.hold_piece = None

        self.score = 0

        matrix = [[(0, 0, 0) for _ in range(10)] for _ in range(23)]
        self.play_grid = Grid.Grid(matrix)

        self.run_game()

    # returns the change in position for a rotation to be valid and returns a
    # tuple with the x and y delta. if there are no possible positions,
    # returns a tuple with None and None
    def get_possible_rotates(self, piece, direction):
        kick_delta = (None, None)
        temp = Piece.Piece(piece.x, piece.y, piece.shape)
        temp.rotation = piece.rotation
        if piece.shape == Piece.I:
            if direction == 'left':
                for pos in Piece.I_WALL_KICK_LEFT[temp.rotation]:
                    temp.x = piece.x + pos[0]
                    temp.y = piece.y - pos[1]
                    if self.valid_move(temp):
                        kick_delta = pos
                        break
            else:
                for pos in Piece.I_WALL_KICK_RIGHT[temp.rotation]:
                    temp.x = piece.x + pos[0]
                    temp.y = piece.y - pos[1]
                    if self.valid_move(temp):
                        kick_delta = pos
                        break
        else:
            if direction == 'left':
                for pos in Piece.WALL_KICK_LEFT[temp.rotation]:
                    temp.x = piece.x + pos[0]
                    temp.y = piece.y - pos[1]
                    if self.valid_move(temp):
                        kick_delta = pos
                        break
            else:
                for pos in Piece.WALL_KICK_RIGHT[temp.rotation]:
                    temp.x = piece.x + pos[0]
                    temp.y = piece.y - pos[1]
                    if self.valid_move(temp):
                        kick_delta = pos
                        break

        return kick_delta

    # checks whether or not the player has lost
    def check_lost(self):
        for pos in self.current_piece.convert_shape_format():
            x, y = pos
            if y >= 3:
                return False
        return True

    # returns a Piece object using 7 bag cycle
    @staticmethod
    def get_shape():
        if len(Piece.SHAPE_Q) == 0:
            for s in Piece.SHAPES:
                Piece.SHAPE_Q.append(s)
        shape = random.choice(Piece.SHAPE_Q)
        Piece.SHAPE_Q.remove(shape)
        return Piece.Piece(3, 0, shape)

    # draws the lines for the play grid
    def draw_grid(self):
        sx = Game.TOP_LEFT_X
        sy = Game.TOP_LEFT_Y

        for i in range(1, len(self.play_grid.grid)):
            pygame.draw.line(self.win, (81, 81, 77), (sx, sy + i * Game.BLOCK_SIZE),
                             (sx + Game.PLAY_WIDTH, sy + i * Game.BLOCK_SIZE))
        for j in range(1, len(self.play_grid.grid[0])):
            pygame.draw.line(self.win, (81, 81, 77), (sx + j * Game.BLOCK_SIZE, sy),
                             (sx + j * Game.BLOCK_SIZE, sy + Game.PLAY_HEIGHT))

    # checks if a row needs to be cleared and moves rows above it down
    def clear_rows(self):
        cleared_below = 0
        for i in range(len(self.play_grid.grid) - 1, 0, -1):
            row = self.play_grid.grid[i]
            if (0, 0, 0) not in row:
                cleared_below += 1
                for j in range(len(row)):
                    del self.locked_positions[(j, i)]
            else:
                for j in range(len(row)):
                    if not (self.play_grid.grid[i][j] == (0, 0, 0)):
                        self.locked_positions[(j, i + cleared_below)] = \
                                              self.locked_positions[(j, i)]
                        if cleared_below > 0:
                            del self.locked_positions[(j, i)]

    # draws the shape in the 'next' area
    def draw_next_shape(self):
        font = pygame.font.SysFont('malgungothicsemilight', 30)
        label = font.render('Next', 1, (255, 255, 255))
        label_w, label_h = font.size('Next')
        sx = (2 * Game.SCREEN_WIDTH - Game.TOP_LEFT_X) / 2 - label_w / 2
        sy = Game.TOP_LEFT_Y
        if self.next_piece.shape == Piece.I or self.next_piece.shape == Piece.O:
            px = (2 * Game.SCREEN_WIDTH - Game.TOP_LEFT_X) / 2 - 2 * Game.BLOCK_SIZE
        else:
            px = (2 * Game.SCREEN_WIDTH - Game.TOP_LEFT_X) / 2 - 1.5 * Game.BLOCK_SIZE
        py = sy + Game.BLOCK_SIZE + label_h
        formatted = self.next_piece.get_piece_format()
        for pair in formatted:
            pygame.draw.rect(self.win, self.next_piece.color, (px + pair[1] * Game.BLOCK_SIZE,
                                                               py + pair[0] * Game.BLOCK_SIZE,
                                                               Game.BLOCK_SIZE, Game.BLOCK_SIZE), 0)
        self.win.blit(label, (sx, sy))

    # returns whether or not the piece is in a valid position
    def valid_move(self, piece):
        formatted = piece.convert_shape_format()
        for pos in formatted:
            if not (0 <= pos[0] < Game.PLAY_WIDTH / Game.BLOCK_SIZE and 0 <= pos[1] <
                    Game.PLAY_HEIGHT / Game.BLOCK_SIZE
                    + 3):
                return False
            if pos[1] >= 0:
                if not (self.play_grid.grid[pos[1]][pos[0]] == (0, 0, 0)):
                    return False
        return True

    # draws the piece in the 'hold' sections
    def draw_hold_piece(self):
        font = pygame.font.SysFont('malgungothicsemilight', 30)
        label = font.render('Hold', 1, (255, 255, 255))
        label_w, label_h = font.size('Hold')
        sx = Game.TOP_LEFT_X / 2 - label_w / 2
        sy = Game.TOP_LEFT_Y
        if self.hold_piece is not None:
            if self.hold_piece.shape == Piece.I or self.hold_piece.shape == Piece.O:
                px = Game.TOP_LEFT_X / 2 - 2 * Game.BLOCK_SIZE
            else:
                px = Game.TOP_LEFT_X / 2 - 1.5 * Game.BLOCK_SIZE
            py = sy + Game.BLOCK_SIZE + label_h
            formatted = self.hold_piece.get_piece_format()
            for pair in formatted:
                pygame.draw.rect(self.win, self.hold_piece.color, (px + pair[1] * Game.BLOCK_SIZE,
                                                                   py + pair[0] * Game.BLOCK_SIZE,
                                                                   Game.BLOCK_SIZE,
                                                                   Game.BLOCK_SIZE), 0)
        self.win.blit(label, (sx, sy))

    def draw_border(self):
        pygame.draw.rect(self.win, (255, 255, 255), (Game.TOP_LEFT_X, Game.TOP_LEFT_Y,
                                                     Game.PLAY_WIDTH, Game.PLAY_HEIGHT), 4)

    # implementation of hard drop feature
    def hard_drop(self, piece):
        piece.y += 1
        while self.valid_move(piece):
            piece.y += 1
        piece.y -= 1

    # returns True if a key is currently pressed, otherwise False
    @staticmethod
    def key_pressed(input_key):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[input_key]:
            return True
        else:
            return False

    # draws
    def draw_window(self):
        self.win.fill((0, 0, 0))
        pygame.font.init()
        font = pygame.font.SysFont('malgungothicsemilight', 60)
        label = font.render('Tetris', 1, (255, 255, 255))

        self.win.blit(label, (Game.TOP_LEFT_X + Game.PLAY_WIDTH / 2 - label.get_width() /
                              2, Game.PLAY_HEIGHT / 25))

        for i in range(len(self.play_grid.grid)):
            for j in range(len(self.play_grid.grid[i])):
                pygame.draw.rect(self.win, self.play_grid.grid[i][j], (Game.TOP_LEFT_X + j *
                                                                       Game.BLOCK_SIZE,
                                                                       Game.TOP_LEFT_Y + (i - 3) *
                                                                       Game.BLOCK_SIZE,
                                                                       Game.BLOCK_SIZE,
                                                                       Game.BLOCK_SIZE), 0)
        self.draw_grid()

    # draw everything
    def render(self):
        self.draw_window()
        self.play_grid.draw_piece_guideline(self.current_piece, self.win, self.locked_positions)
        self.draw_border()
        self.draw_next_shape()
        self.draw_hold_piece()

    # main game logic
    def run_game(self):
        while self.run:
            self.play_grid.update_grid(self.locked_positions)
            self.fall_time += self.clock.get_rawtime()
            self.clock.tick()
            if self.is_lock:
                self.lock_time += self.clock.get_rawtime()
                if self.current_piece.y > self.lock_y + 3:
                    self.lock_time = 0
                    self.is_lock = False
                    self.rotate_count = 0

            # timer check for auto dropping
            if self.fall_time / 1000 > self.fall_speed:
                self.fall_time = 0
                self.current_piece.y += 1
                if not (self.valid_move(self.current_piece)) and self.current_piece.y > -1:
                    self.current_piece.y -= 1
                    if self.is_lock is False:
                        self.lock_y = self.current_piece.y
                    self.is_lock = True
                    if self.lock_time / 1000 > self.lock_delay:
                        if self.check_lost():
                            self.run = False
                        else:
                            self.change_piece = True
                        self.is_lock = False
                        self.lock_time = 0
                        self.rotate_count = 0

            # if down key is pressed, just speed up auto drop, same as soft drop
            if self.key_pressed(pygame.K_DOWN):
                self.fall_speed = 0.03
            else:
                self.fall_speed = 0.6

            # if we need to change the piece, do so and update the locked positions
            if self.change_piece:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    self.locked_positions[p] = self.current_piece.color
                self.play_grid.update_grid(self.locked_positions)
                self.current_piece = self.next_piece
                self.next_piece = self.get_shape()
                self.change_piece = False
                self.clear_rows()
                self.fall_time = 10000
                self.is_hold = False

            # check keypresses and end game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                if event.type == pygame.KEYDOWN:  # move left
                    if event.key == pygame.K_LEFT:
                        self.current_piece.x -= 1
                        if not (self.valid_move(self.current_piece)):
                            self.current_piece.x += 1
                    if event.key == pygame.K_RIGHT:  # move right
                        self.current_piece.x += 1
                        if not (self.valid_move(self.current_piece)):
                            self.current_piece.x -= 1
                    if event.key == pygame.K_z:  # rotate left
                        if self.is_lock:
                            self.rotate_count += 1
                        if self.rotate_count < 10:
                            self.lock_time = 0
                        self.current_piece.rotate_left()
                        # check wall kick data
                        delta = self.get_possible_rotates(self.current_piece, 'left')
                        if delta == (None, None):
                            self.current_piece.rotate_right()
                        else:
                            self.current_piece.x += delta[0]
                            self.current_piece.y -= delta[1]
                    if event.key == pygame.K_x:  # rotate right
                        if self.is_lock:
                            self.rotate_count += 1
                        if self.rotate_count < 10:
                            self.lock_time = 0
                        self.current_piece.rotate_right()
                        # check wall kick data
                        delta = self.get_possible_rotates(self.current_piece, 'right')
                        if delta == (None, None):
                            self.current_piece.rotate_left()
                        else:
                            self.current_piece.x += delta[0]
                            self.current_piece.y -= delta[1]
                    # hard drop
                    if event.key == pygame.K_SPACE:
                        self.rotate_count = 0
                        self.lock_time = 0
                        self.is_lock = False
                        self.hard_drop(self.current_piece)
                        if not self.check_lost():
                            self.change_piece = True
                    # hold piece
                    if event.key == pygame.K_c:
                        # would implement as function but python pass by
                        # reference or whatever it is is weird
                        if not self.is_hold:
                            self.rotate_count = 0
                            self.lock_time = 0
                            self.is_lock = False
                            if self.hold_piece is None:
                                self.hold_piece = self.current_piece
                                self.hold_piece.x = 3
                                self.hold_piece.y = 0
                                self.hold_piece.rotation = 0
                                self.current_piece = self.next_piece
                                self.next_piece = self.get_shape()
                            else:
                                temp = self.current_piece
                                self.current_piece = self.hold_piece
                                self.hold_piece = temp
                                self.hold_piece.x = 3
                                self.hold_piece.y = 0
                                self.hold_piece.rotation = 0
                            self.is_hold = True

            shape_pos = self.current_piece.convert_shape_format()

            # update grid with current piece position
            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                self.play_grid.grid[y][x] = self.current_piece.color

            self.render()

            # update screen
            pygame.display.update()
        self.reset()
