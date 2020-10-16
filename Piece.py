import copy

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


# class for Tetrominoes
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    # rotate piece left 90 degrees
    def rotate_left(self):
        if self.rotation == 0:
            self.rotation = 3
        else:
            self.rotation -= 1

    # rotate piece right 90 degrees
    def rotate_right(self):
        if self.rotation == 3:
            self.rotation = 0
        else:
            self.rotation += 1

    # returns the list of positions of each mino in the tetromino relative to
    # itself after calculating the rotation
    def get_piece_format(self):
        f = copy.deepcopy(self.shape)
        if f != O:
            for i in range(self.rotation):
                for pair in f:
                    temp = pair[0]
                    pair[0] = pair[1]
                    pair[1] = temp
                if self.shape == I:
                    for pair in f:
                        pair[1] = 3 - pair[1]
                else:
                    for pair in f:
                        pair[1] = 2 - pair[1]
        return f

    # returns the position of each mino in the tetromino relative to the top
    # left corner of the screen
    def convert_shape_format(self):
        piece_format = self.get_piece_format()
        positions = []
        for pair in piece_format:
            positions.append((self.x + pair[1], self.y + pair[0]))

        return positions
