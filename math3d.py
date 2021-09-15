import math


class Matrix3x3:
    def __init__(self, rows: list=None):
        # generate empty matrix
        self.data = [[0, 0, 0] for _ in range(3)]

        if isinstance(rows, list) and len(rows) == 3 and set(map(len, rows)) == {3}:
            # valid 2d list
            if all(isinstance(value, (int, float)) for row in rows for value in row):
                # all values are actually numbers
                self.data = rows

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            new = self.__class__()
            for y in range(3):
                for x in range(3):
                    # matrix multiplication
                    paired = zip(self.data[y], [i[x] for i in other.data])
                    new.data[y][x] = sum(map(lambda i: i[0] * i[1], paired))

            return new

        if isinstance(other, (int, float)):
            new = self.__class__()
            for y in range(3):
                for x in range(3):
                    # scalar multiplication
                    new.data[y][x] = self.data[y][x] * other

            return new

        # raised when multiplying with wrong types
        return NotImplemented


class Vector3(Matrix3x3):
    def __init__(self, i: float=0, j: float=0, k: float=0):
        # Vectors are represented as matrices to allow easy matrix - vector multiplication
        try:
            # test that values entered are actually numbers, otherwise create a zero vector
            assert isinstance(i, (int, float))
            assert isinstance(j, (int, float))
            assert isinstance(k, (int, float))
            self.data = [[i, 0, 0], [j, 0, 0], [k, 0, 0]]

        except AssertionError:
            self.data = [[0, 0, 0] for _ in range(3)]

    def __add__(self, other):
        if isinstance(other, self.__class__):
            new = self.__class__()
            new.i = self.i + other.i
            new.j = self.j + other.j
            new.k = self.k + other.k

    @property
    def i(self):
        return self.data[0][0]

    @i.setter
    def i(self, value):
        self.data[0][0] = value

    @property
    def j(self):
        return self.data[1][0]

    @j.setter
    def j(self, value):
        self.data[1][0] = value
    @property
    def k(self):
        return self.data[2][0]

    @k.setter
    def k(self, value):
        self.data[2][0] = value

    @property
    def magnitude(self):
        return math.sqrt(self.i ** 2 + self.j ** 2 + self.k ** 2)


# matrices to rotate a point in 3D space
def rot_x(deg: float) -> Matrix3x3:
    return Matrix3x3([
        [1, 0, 0],
        [0, math.cos(math.radians(deg)), math.sin(math.radians(deg))],
        [0, -math.sin(math.radians(deg)), math.cos(math.radians(deg))]
    ])


def rot_y(deg: float) -> Matrix3x3:
    return Matrix3x3([
        [math.cos(math.radians(deg)), 0, -math.sin(math.radians(deg))],
        [0, 1, 0],
        [math.sin(math.radians(deg)), 0, math.cos(math.radians(deg))]
    ])


def rot_z(deg: float) -> Matrix3x3:
    return Matrix3x3([
        [math.cos(math.radians(deg)), math.sin(math.radians(deg)), 0],
        [-math.sin(math.radians(deg)), math.cos(math.radians(deg)), 0],
        [0, 0, 1]
    ])


class Triangle:
    def __init__(self, p1: Vector3, p2: Vector3, p3: Vector3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
