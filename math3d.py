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
