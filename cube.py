from math3d import Mesh, Triangle, Vector3, rot_x, rot_y, rot_z
import re

hex_col = re.compile(r"#[\dA-Za-z]{6}")


def rotate_2darray(arr):
    return list(map(list, zip(*arr[::-1])))


class Center(Mesh):
    def __init__(self, pos: Vector3, col: str, width: float):
        # replace invalid colours with white
        try:
            assert hex_col.match(col) is not None

        except AssertionError:
            col = "#ffffff"

        self.col = col
        self.triangles = [
            # top
            Triangle(Vector3(1, 1, -1), Vector3(-1, 1, -1), Vector3(-1, 1, 1), col),
            Triangle(Vector3(-1, 1, 1), Vector3(1, 1, 1), Vector3(1, 1, -1), col)
        ]

        self.scale(width / 2)
        self.translate(pos)

        self.width = width
        self.pos = pos

    def copy(self) -> object:
        new = self.__class__(self.pos, self.col, self.width)
        new.triangles = []
        for tri in self.triangles:
            new.triangles.append(Triangle(tri.p1.copy(), tri.p2.copy(), tri.p3.copy(), tri.col))

        return new


class Edge(Mesh):
    def __init__(self, pos: Vector3, col1: str, col2: str, width: float):
        # replace invalid colours with white
        try:
            assert hex_col.match(col1) is not None
            assert hex_col.match(col2) is not None

        except AssertionError:
            col1 = col2 = "#ffffff"

        self.col1 = col1
        self.col2 = col2
        self.triangles = [
            # top
            Triangle(Vector3(1, 1, -1), Vector3(-1, 1, -1), Vector3(-1, 1, 1), col1),
            Triangle(Vector3(-1, 1, 1), Vector3(1, 1, 1), Vector3(1, 1, -1), col1),
            # front
            Triangle(Vector3(1, -1, -1), Vector3(-1, -1, -1), Vector3(-1, 1, -1), col2),
            Triangle(Vector3(-1, 1, -1), Vector3(1, 1, -1), Vector3(1, -1, -1), col2)
        ]

        self.scale(width / 2)
        self.translate(pos)

        self.width = width
        self.pos = pos

    def copy(self) -> object:
        new = self.__class__(self.pos, self.col1, self.col2, self.width)
        new.triangles = []
        for tri in self.triangles:
            new.triangles.append(Triangle(tri.p1.copy(), tri.p2.copy(), tri.p3.copy(), tri.col))

        return new


class Corner(Mesh):
    def __init__(self, pos: Vector3, col1: str, col2: str, col3: str, width: float):
        # replace invalid colours with white
        try:
            assert hex_col.match(col1) is not None
            assert hex_col.match(col2) is not None
            assert hex_col.match(col3) is not None

        except AssertionError:
            col1 = col2 = col3 = "#ffffff"

        self.col1 = col1
        self.col2 = col2
        self.col3 = col3
        self.triangles = [
            # top
            Triangle(Vector3(1, 1, -1), Vector3(-1, 1, -1), Vector3(-1, 1, 1), col1),
            Triangle(Vector3(-1, 1, 1), Vector3(1, 1, 1), Vector3(1, 1, -1), col1),
            # front
            Triangle(Vector3(1, -1, -1), Vector3(-1, -1, -1), Vector3(-1, 1, -1), col2),
            Triangle(Vector3(-1, 1, -1), Vector3(1, 1, -1), Vector3(1, -1, -1), col2),
            # right
            Triangle(Vector3(1, -1, 1), Vector3(1, -1, -1), Vector3(1, 1, -1), col3),
            Triangle(Vector3(1, 1, -1), Vector3(1, 1, 1), Vector3(1, -1, 1), col3)
        ]

        self.scale(width / 2)
        self.translate(pos)

        self.width = width
        self.pos = pos

    def copy(self) -> object:
        new = self.__class__(self.pos, self.col1, self.col2, self.col3, self.width)
        new.triangles = []
        for tri in self.triangles:
            new.triangles.append(Triangle(tri.p1.copy(), tri.p2.copy(), tri.p3.copy(), tri.col))

        return new


class RubiksCube:
    def __init__(self, width: float, layers: int):
        white = "#ffffff"
        yellow = "#ffff00"
        red = "#ff0000"
        orange = "#ff6f00"
        blue = "#0000ff"
        green = "#00ff00"

        layers = int(layers)
        self.layers = layers

        try:
            assert layers > 1
            assert isinstance(width, (int, float))

        except AssertionError:
            layers = 2
            width = 12

        piece_width = width / layers

        delta = piece_width * (layers // 2) - (0 if layers % 2 else piece_width / 2)

        # values to adjust edge piece placement with different size cubes
        edge_align = 0 if layers % 2 else 0.5
        d_edge = piece_width * (layers // 2) - piece_width * edge_align

        self.pieces = []
        for z in range(layers):
            z_layer = []
            for y in range(layers):
                y_layer = []
                for x in range(layers):
                    if z == 0:
                        if y == 0:
                            if x == 0:
                                # front bottom left corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), yellow, red, green, piece_width))
                                y_layer[-1].rotate(rot_z(180))

                            elif x == layers - 1:
                                # front bottom right corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), blue, red, yellow, piece_width))
                                y_layer[-1].rotate(rot_z(90))

                            else:
                                # front bottom edges
                                y_layer.append(Edge(Vector3(d_edge - x * piece_width, delta, -delta), yellow, red, piece_width))
                                y_layer[-1].rotate(rot_z(180))

                        elif y == layers - 1:
                            if x == 0:
                                # front top left corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), white, green, red, piece_width))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # front top right corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), white, red, blue, piece_width))

                            else:
                                # front top edges
                                y_layer.append(Edge(Vector3(x * piece_width - d_edge, delta, -delta), white, red, piece_width))

                        else:
                            if x == 0:
                                # front middle left edges
                                y_layer.append(Edge(Vector3(y * piece_width - d_edge, delta, -delta), green, red, piece_width))
                                y_layer[-1].rotate(rot_z(-90))

                            elif x == layers - 1:
                                # front middle right edges
                                y_layer.append(Edge(Vector3(d_edge - y * piece_width, delta, -delta), blue, red, piece_width))
                                y_layer[-1].rotate(rot_z(90))

                            else:
                                # front center
                                y_layer.append(Center(Vector3(x * piece_width - d_edge, delta, y * piece_width - d_edge), red, piece_width))
                                y_layer[-1].rotate(rot_x(90))

                    elif z == layers - 1:
                        if y == 0:
                            if x == 0:
                                # back bottom left corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), yellow, green, orange, piece_width))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # back bottom right corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), yellow, orange, blue, piece_width))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(180))

                            else:
                                # back bottom edges
                                y_layer.append(Edge(Vector3(x * piece_width - d_edge, delta, -delta), yellow, orange, piece_width))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(180))

                        elif y == layers - 1:
                            if x == 0:
                                # back top left corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), white, orange, green, piece_width))
                                y_layer[-1].rotate(rot_y(180))

                            elif x == layers - 1:
                                # back top right corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), white, blue, orange, piece_width))
                                y_layer[-1].rotate(rot_y(90))

                            else:
                                # back top edges
                                y_layer.append(Edge(Vector3(d_edge - x * piece_width, delta, -delta), white, orange, piece_width))
                                y_layer[-1].rotate(rot_y(180))

                        else:
                            if x == 0:
                                # back left edges
                                y_layer.append(Edge(Vector3(d_edge - y * piece_width, delta, -delta), green, orange, piece_width))
                                y_layer[-1].rotate(rot_z(90))
                                y_layer[-1].rotate(rot_y(180))

                            elif x == layers - 1:
                                # back right edges
                                y_layer.append(Edge(Vector3(y * piece_width - d_edge, delta, -delta), blue, orange, piece_width))
                                y_layer[-1].rotate(rot_z(-90))
                                y_layer[-1].rotate(rot_y(180))

                            else:
                                # back center
                                y_layer.append(Center(Vector3(x * piece_width - d_edge, delta, d_edge - y * piece_width), orange, piece_width))
                                y_layer[-1].rotate(rot_x(-90))

                    else:
                        if y == 0:
                            if x == 0:
                                # middle bottom left edges
                                y_layer.append(Edge(Vector3(z * piece_width - d_edge, delta, -delta), yellow, green, piece_width))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # middle bottom right edges
                                y_layer.append(Edge(Vector3(d_edge - z * piece_width, delta, -delta), yellow, blue, piece_width))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(90))

                            else:
                                # bottom center
                                y_layer.append(Center(Vector3(d_edge - x * piece_width, delta, z * piece_width - d_edge), yellow, piece_width))
                                y_layer[-1].rotate(rot_z(180))

                        elif y == layers - 1:
                            if x == 0:
                                # middle top left edges
                                y_layer.append(Edge(Vector3(d_edge - z * piece_width, delta, -delta), white, green, piece_width))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # middle top right edges
                                y_layer.append(Edge(Vector3(z * piece_width - d_edge, delta, -delta), white, blue, piece_width))
                                y_layer[-1].rotate(rot_y(90))

                            else:
                                # top center
                                y_layer.append(Center(Vector3(x * piece_width - d_edge, delta, z * piece_width - d_edge), white, piece_width))

                        else:
                            if x == 0:
                                # left center
                                y_layer.append(Center(Vector3(y * piece_width - d_edge, delta, z * piece_width - d_edge), green, piece_width))
                                y_layer[-1].rotate(rot_z(-90))

                            elif x == layers - 1:
                                # right center
                                y_layer.append(Center(Vector3(d_edge - y * piece_width, delta, z * piece_width - d_edge), blue, piece_width))
                                y_layer[-1].rotate(rot_z(90))

                            else:
                                # interior pieces
                                y_layer.append(None)

                z_layer.append(y_layer)

            self.pieces.append(z_layer)

    def rotate(self, pattern: str) -> None:
        if pattern == "F":
            # rotate pieces in scene
            [self.pieces[0][i][j].rotate(rot_z(90)) for i in range(self.layers) for j in range(self.layers)]

            # update corner positions
            tmp = self.pieces[0][0][0]
            self.pieces[0][0][0] = self.pieces[0][0][self.layers - 1]
            self.pieces[0][0][self.layers - 1] = self.pieces[0][self.layers - 1][self.layers - 1]
            self.pieces[0][self.layers - 1][self.layers - 1] = self.pieces[0][self.layers - 1][0]
            self.pieces[0][self.layers - 1][0] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[0][0][i]
                self.pieces[0][0][i] = self.pieces[0][i][self.layers - 1]
                self.pieces[0][i][self.layers - 1] = self.pieces[0][self.layers - 1][self.layers - i - 1]
                self.pieces[0][self.layers - 1][self.layers - i - 1] = self.pieces[0][self.layers - i - 1][0]
                self.pieces[0][self.layers - i - 1][0] = tmp

        elif pattern == "B":
            # rotate pieces in scene
            [self.pieces[self.layers - 1][i][j].rotate(rot_z(-90)) for i in range(self.layers) for j in range(self.layers)]

            # update corner positions
            tmp = self.pieces[self.layers - 1][0][self.layers - 1]
            self.pieces[self.layers - 1][0][self.layers - 1] = self.pieces[self.layers - 1][0][0]
            self.pieces[self.layers - 1][0][0] = self.pieces[self.layers - 1][self.layers - 1][0]
            self.pieces[self.layers - 1][self.layers - 1][0] = self.pieces[self.layers - 1][self.layers - 1][self.layers - 1]
            self.pieces[self.layers - 1][self.layers - 1][self.layers - 1] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[self.layers - 1][0][self.layers - i - 1]
                self.pieces[self.layers - 1][0][self.layers - i - 1] = self.pieces[self.layers - 1][i][0]
                self.pieces[self.layers - 1][i][0] = self.pieces[self.layers - 1][self.layers - 1][self.layers - i - 1]
                self.pieces[self.layers - 1][self.layers - 1][self.layers - i - 1] = self.pieces[self.layers - 1][self.layers - i - 1][self.layers - 1]
                self.pieces[self.layers - 1][self.layers - i - 1][self.layers - 1] = tmp

        elif pattern == "R":
            # rotate pieces in scene
            [self.pieces[i][j][self.layers - 1].rotate(rot_x(-90)) for i in range(self.layers) for j in range(self.layers)]

            # update corner positions
            tmp = self.pieces[0][0][self.layers - 1]
            self.pieces[0][0][self.layers - 1] = self.pieces[self.layers - 1][0][self.layers - 1]
            self.pieces[self.layers - 1][0][self.layers - 1] = self.pieces[self.layers - 1][self.layers - 1][self.layers - 1]
            self.pieces[self.layers - 1][self.layers - 1][self.layers - 1] = self.pieces[0][self.layers - 1][self.layers - 1]
            self.pieces[0][self.layers - 1][self.layers - 1] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[i][0][self.layers - 1]
                self.pieces[i][0][self.layers - 1] = self.pieces[self.layers - 1][i][self.layers - 1]
                self.pieces[self.layers - 1][i][self.layers - 1] = self.pieces[self.layers - i - 1][self.layers - 1][self.layers - 1]
                self.pieces[self.layers - i - 1][self.layers - 1][self.layers - 1] = self.pieces[0][self.layers - i - 1][self.layers - 1]
                self.pieces[0][self.layers - i - 1][self.layers - 1] = tmp

        elif pattern == "L":
            # rotate pieces in scene
            [self.pieces[i][j][0].rotate(rot_x(90)) for i in range(self.layers) for j in range(self.layers)]

            # update corner positions
            tmp = self.pieces[self.layers - 1][0][0]
            self.pieces[self.layers - 1][0][0] = self.pieces[0][0][0]
            self.pieces[0][0][0] = self.pieces[0][self.layers - 1][0]
            self.pieces[0][self.layers - 1][0] = self.pieces[self.layers - 1][self.layers - 1][0]
            self.pieces[self.layers - 1][self.layers - 1][0] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[self.layers - i - 1][0][0]
                self.pieces[self.layers - i - 1][0][0] = self.pieces[0][i][0]
                self.pieces[0][i][0] = self.pieces[i][self.layers - 1][0]
                self.pieces[i][self.layers - 1][0] = self.pieces[self.layers - 1][self.layers - i - 1][0]
                self.pieces[self.layers - 1][self.layers - i - 1][0] = tmp

        elif pattern == "U":
            # rotate pieces in scene
            [self.pieces[i][self.layers - 1][j].rotate(rot_y(-90)) for i in range(self.layers) for j in range(self.layers)]

            # update corner positions
            tmp = self.pieces[0][self.layers - 1][0]
            self.pieces[0][self.layers - 1][0] = self.pieces[0][self.layers - 1][self.layers - 1]
            self.pieces[0][self.layers - 1][self.layers - 1] = self.pieces[self.layers - 1][self.layers - 1][self.layers - 1]
            self.pieces[self.layers - 1][self.layers - 1][self.layers - 1] = self.pieces[self.layers - 1][self.layers - 1][0]
            self.pieces[self.layers - 1][self.layers - 1][0] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[0][self.layers - 1][i]
                self.pieces[0][self.layers - 1][i] = self.pieces[i][self.layers - 1][self.layers - 1]
                self.pieces[i][self.layers - 1][self.layers - 1] = self.pieces[self.layers - 1][self.layers - 1][self.layers - i - 1]
                self.pieces[self.layers - 1][self.layers - 1][self.layers - i - 1] = self.pieces[self.layers - i - 1][self.layers - 1][0]
                self.pieces[self.layers - i - 1][self.layers - 1][0] = tmp

        elif pattern == "D":
            # rotate pieces in scene
            [self.pieces[i][0][j].rotate(rot_y(90)) for i in range(self.layers) for j in range(self.layers)]

            # update corner positions
            tmp = self.pieces[self.layers - 1][0][0]
            self.pieces[self.layers - 1][0][0] = self.pieces[self.layers - 1][0][self.layers - 1]
            self.pieces[self.layers - 1][0][self.layers - 1] = self.pieces[0][0][self.layers - 1]
            self.pieces[0][0][self.layers - 1] = self.pieces[0][0][0]
            self.pieces[0][0][0] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[self.layers - 1][0][i]
                self.pieces[self.layers - 1][0][i] = self.pieces[self.layers - i - 1][0][self.layers - 1]
                self.pieces[self.layers - i - 1][0][self.layers - 1] = self.pieces[0][0][self.layers - i - 1]
                self.pieces[0][0][self.layers - i - 1] = self.pieces[i][0][0]
                self.pieces[i][0][0] = tmp

        elif pattern.endswith("'"):
            # reverse patterns, anti-clockwise instead of clockwise
            [self.rotate(pattern[:-1]) for _ in range(3)]

        elif pattern.endswith("2"):
            # 180 degree turn
            [self.rotate(pattern[:-1]) for _ in range(2)]


    def slice(self, face: str, depth: int) -> None:
        if face.endswith("'"):
            # anti-clockwise rotation
            [self.slice(face[:-1], depth) for _ in range(3)]

        if depth >= self.layers:
            # if depth to large rotate the first piece
            depth = 0

        if depth == 0:
            # rotating front face
            self.rotate(face)

        elif depth == self.layers - 1:
            # rotating reverse face
            opposite = {"F": "B'", "B": "F'", "R": "L'", "L": "R'", "U": "D'", "D": "U'"}
            self.rotate(opposite[face])

        elif face == "F":
            for i in range(self.layers):
                for j in range(self.layers):
                    if self.pieces[depth][i][j] is not None:
                        # rotate pieces in scene
                        self.pieces[depth][i][j].rotate(rot_z(90))

            # update corner positions
            tmp = self.pieces[depth][0][0]
            self.pieces[depth][0][0] = self.pieces[depth][0][self.layers - 1]
            self.pieces[depth][0][self.layers - 1] = self.pieces[depth][self.layers - 1][self.layers - 1]
            self.pieces[depth][self.layers - 1][self.layers - 1] = self.pieces[depth][self.layers - 1][0]
            self.pieces[depth][self.layers - 1][0] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[depth][0][i]
                self.pieces[depth][0][i] = self.pieces[depth][i][self.layers - 1]
                self.pieces[depth][i][self.layers - 1] = self.pieces[depth][self.layers - 1][self.layers - i - 1]
                self.pieces[depth][self.layers - 1][self.layers - i - 1] = self.pieces[depth][self.layers - i - 1][0]
                self.pieces[depth][self.layers - i - 1][0] = tmp

        elif face == "B":
            depth = self.layers - 1 - depth
            for i in range(self.layers):
                for j in range(self.layers):
                    if self.pieces[depth][i][j] is not None:
                        # rotate pieces in scene
                        self.pieces[depth][i][j].rotate(rot_z(-90))

            # update corner positions
            tmp = self.pieces[depth][0][0]
            self.pieces[depth][0][0] = self.pieces[depth][0][self.layers - 1]
            self.pieces[depth][0][self.layers - 1] = self.pieces[depth][self.layers - 1][self.layers - 1]
            self.pieces[depth][self.layers - 1][self.layers - 1] = self.pieces[depth][self.layers - 1][0]
            self.pieces[depth][self.layers - 1][0] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[depth][0][i]
                self.pieces[depth][0][i] = self.pieces[depth][i][self.layers - 1]
                self.pieces[depth][i][self.layers - 1] = self.pieces[depth][self.layers - 1][self.layers - i - 1]
                self.pieces[depth][self.layers - 1][self.layers - i - 1] = self.pieces[depth][self.layers - i - 1][0]
                self.pieces[depth][self.layers - i - 1][0] = tmp

        elif face == "R":
            depth = self.layers - 1 - depth
            for i in range(self.layers):
                for j in range(self.layers):
                    if self.pieces[i][j][depth] is not None:
                        # rotate pieces in scene
                        self.pieces[i][j][depth].rotate(rot_x(-90))

            # update corner positions
            tmp = self.pieces[0][0][depth]
            self.pieces[0][0][depth] = self.pieces[self.layers - 1][0][depth]
            self.pieces[self.layers - 1][0][depth] = self.pieces[self.layers - 1][self.layers - 1][depth]
            self.pieces[self.layers - 1][self.layers - 1][depth] = self.pieces[0][self.layers - 1][depth]
            self.pieces[0][self.layers - 1][depth] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[i][0][depth]
                self.pieces[i][0][depth] = self.pieces[self.layers - 1][i][depth]
                self.pieces[self.layers - 1][i][depth] = self.pieces[self.layers - i - 1][self.layers - 1][depth]
                self.pieces[self.layers - i - 1][self.layers - 1][depth] = self.pieces[0][self.layers - i - 1][depth]
                self.pieces[0][self.layers - i - 1][depth] = tmp

        elif face == "L":
            for i in range(self.layers):
                for j in range(self.layers):
                    if self.pieces[i][j][depth] is not None:
                        # rotate pieces in scene
                        self.pieces[i][j][depth].rotate(rot_x(90))

            # update corner positions
            tmp = self.pieces[self.layers - 1][0][depth]
            self.pieces[self.layers - 1][0][depth] = self.pieces[0][0][depth]
            self.pieces[0][0][depth] = self.pieces[0][self.layers - 1][depth]
            self.pieces[0][self.layers - 1][depth] = self.pieces[self.layers - 1][self.layers - 1][depth]
            self.pieces[self.layers - 1][self.layers - 1][depth] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[self.layers - i - 1][0][depth]
                self.pieces[self.layers - i - 1][0][depth] = self.pieces[0][i][depth]
                self.pieces[0][i][depth] = self.pieces[i][self.layers - 1][depth]
                self.pieces[i][self.layers - 1][depth] = self.pieces[self.layers - 1][self.layers - i - 1][depth]
                self.pieces[self.layers - 1][self.layers - i - 1][depth] = tmp

        elif face == "U":
            depth = self.layers - depth - 1
            for i in range(self.layers):
                for j in range(self.layers):
                    if self.pieces[i][depth][j] is not None:
                        # rotate pieces in scene
                        self.pieces[i][depth][j].rotate(rot_y(-90))

            # update corner positions
            tmp = self.pieces[0][depth][0]
            self.pieces[0][depth][0] = self.pieces[0][depth][self.layers - 1]
            self.pieces[0][depth][self.layers - 1] = self.pieces[self.layers - 1][depth][self.layers - 1]
            self.pieces[self.layers - 1][depth][self.layers - 1] = self.pieces[self.layers - 1][depth][0]
            self.pieces[self.layers - 1][depth][0] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[0][depth][i]
                self.pieces[0][depth][i] = self.pieces[i][depth][self.layers - 1]
                self.pieces[i][depth][self.layers - 1] = self.pieces[self.layers - 1][depth][self.layers - i - 1]
                self.pieces[self.layers - 1][depth][self.layers - i - 1] = self.pieces[self.layers - i - 1][depth][0]
                self.pieces[self.layers - i - 1][depth][0] = tmp

        elif face == "D":
            for i in range(self.layers):
                for j in range(self.layers):
                    if self.pieces[i][depth][j] is not None:
                        # rotate pieces in scene
                        self.pieces[i][depth][j].rotate(rot_y(90))

            # update corner positions
            tmp = self.pieces[self.layers - 1][depth][0]
            self.pieces[self.layers - 1][depth][0] = self.pieces[self.layers - 1][depth][self.layers - 1]
            self.pieces[self.layers - 1][depth][self.layers - 1] = self.pieces[0][depth][self.layers - 1]
            self.pieces[0][depth][self.layers - 1] = self.pieces[0][depth][0]
            self.pieces[0][depth][0] = tmp

            # update edge positions
            for i in range(1, self.layers - 1):
                tmp = self.pieces[self.layers - 1][depth][i]
                self.pieces[self.layers - 1][depth][i] = self.pieces[self.layers - i - 1][depth][self.layers - 1]
                self.pieces[self.layers - i - 1][depth][self.layers - 1] = self.pieces[0][depth][self.layers - i - 1]
                self.pieces[0][depth][self.layers - i - 1] = self.pieces[i][depth][0]
                self.pieces[i][depth][0] = tmp
