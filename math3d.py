class Matrix3x3:
    def __init__(self, rows: list=None):
        if isinstance(rows, list) and len(rows) == 3 and set(map(len, rows)) == {3}:
            # valid 2d list
            self.data = rows

        else:
            # generate empty matrix
            self.data = [[0, 0, 0] for _ in range(3)]

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            new = self.__class__()
            for y in range(3):
                for x in range(3):
                    # matrix multiplication (sum(row * col))
                    paired = zip(self.data[y], [i[x] for i in other.data])
                    value = sum(map(lambda i: i[0] * i[1], paired))
                    new.data[y][x] = value

            return new

        # raised when multiplying with wrong types
        return NotImplemented


class Vector3(Matrix3x3):
    def __init__(self, i: float=0, j: float=0, k: float=0):
        # Vectors are represented as matrices to allow easy matrix - vector multiplication
        assert isinstance(i, (int, float))
        assert isinstance(j, (int, float))
        assert isinstance(k, (int, float))
        self.data = [[i, 0, 0], [j, 0, 0], [k, 0, 0]]

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
