from math3d import Matrix3x3, Mesh, Polygon, Triangle, Vector3, rot_x, rot_y, rot_z
import random, re, threading, time

hex_col = re.compile(r"#[\dA-Za-z]{6}")


def rotate_2darray(arr):
    return list(map(list, zip(*arr[::-1])))


class Move:
    def __init__(self, face: str, turns: int=1, depth: int=0):
        self.face = face
        self.turns = turns % 4 if turns % 4 else 1  # minimun turn is 1
        self.depth = depth

    def __repr__(self):
        return self.face + str(self.turns) + (str(self.depth) if self.depth else "")


class Center(Mesh):
    def __init__(self, pos: Vector3, col: str, width: float):
        # replace invalid colours with white
        try:
            assert hex_col.match(col) is not None

        except AssertionError:
            col = "#ffffff"

        self.col = col
        self.polys = [Polygon(
            # top
            Triangle(Vector3(1, 1, -1), Vector3(-1, 1, -1), Vector3(-1, 1, 1), col),
            Triangle(Vector3(-1, 1, 1), Vector3(1, 1, 1), Vector3(1, 1, -1), col)
        )]

        self.scale(width / 2)
        self.translate(pos)

        self.width = width
        self.pos = pos

    def copy(self) -> object:
        new = self.__class__(self.pos, self.col, self.width)
        new.polys = []
        for poly in self.polys:
            new_poly = Polygon()
            for tri in poly.triangles:
                new_poly.triangles.append(Triangle(tri.p1.copy(), tri.p2.copy(), tri.p3.copy(), tri.col))

            new.polys.append(new_poly)

        return new


class Edge(Mesh):
    def __init__(self, pos: Vector3, col1: str, col2: str, width: float, orient: int):
        # replace invalid colours with white
        try:
            assert hex_col.match(col1) is not None
            assert hex_col.match(col2) is not None

        except AssertionError:
            col1 = col2 = "#ffffff"

        self.col1 = col1
        self.col2 = col2
        self.polys = [
            # top
            Polygon(
                Triangle(Vector3(1, 1, -1), Vector3(-1, 1, -1), Vector3(-1, 1, 1), col1),
                Triangle(Vector3(-1, 1, 1), Vector3(1, 1, 1), Vector3(1, 1, -1), col1),
            ),
            # front
            Polygon(
                Triangle(Vector3(1, -1, -1), Vector3(-1, -1, -1), Vector3(-1, 1, -1), col2),
                Triangle(Vector3(-1, 1, -1), Vector3(1, 1, -1), Vector3(1, -1, -1), col2)
            )
        ]

        self.scale(width / 2)
        self.translate(pos)

        self.width = width
        self.pos = pos
        self.orient = orient

    def copy(self) -> object:
        new = self.__class__(self.pos, self.col1, self.col2, self.width, self.orient)
        new.polys = []
        for poly in self.polys:
            new_poly = Polygon()
            for tri in poly.triangles:
                new_poly.triangles.append(Triangle(tri.p1.copy(), tri.p2.copy(), tri.p3.copy(), tri.col))

            new.polys.append(new_poly)

        return new


class Corner(Mesh):
    def __init__(self, pos: Vector3, col1: str, col2: str, col3: str, width: float, orient: int):
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
        self.polys = [
            # top
            Polygon(
                Triangle(Vector3(1, 1, -1), Vector3(-1, 1, -1), Vector3(-1, 1, 1), col1),
                Triangle(Vector3(-1, 1, 1), Vector3(1, 1, 1), Vector3(1, 1, -1), col1),
            ),
            # front
            Polygon(
                Triangle(Vector3(1, -1, -1), Vector3(-1, -1, -1), Vector3(-1, 1, -1), col2),
                Triangle(Vector3(-1, 1, -1), Vector3(1, 1, -1), Vector3(1, -1, -1), col2),
            ),
            # right
            Polygon(
                Triangle(Vector3(1, -1, 1), Vector3(1, -1, -1), Vector3(1, 1, -1), col3),
                Triangle(Vector3(1, 1, -1), Vector3(1, 1, 1), Vector3(1, -1, 1), col3)
            )
        ]

        self.scale(width / 2)
        self.translate(pos)

        self.width = width
        self.pos = pos
        self.orient = orient

    def copy(self) -> object:
        new = self.__class__(self.pos, self.col1, self.col2, self.col3, self.width, self.orient)
        new.polys = []
        for poly in self.polys:
            new_poly = Polygon()
            for tri in poly.triangles:
                new_poly.triangles.append(Triangle(tri.p1.copy(), tri.p2.copy(), tri.p3.copy(), tri.col))

            new.polys.append(new_poly)

        return new


class RubiksCube:
    def __init__(self, width: float, layers: int, turn_duration: float, display: bool):
        self.white = "#ffffff"
        self.yellow = "#ffff00"
        self.red = "#ff0000"
        self.orange = "#ff6f00"
        self.blue = "#0000ff"
        self.green = "#00ff00"

        # dimmed colours for when face is selected
        self.dimmed = {
            self.white: "#cccccc",
            self.yellow: "#999900",
            self.red: "#990000",
            self.orange: "#994300",
            self.blue: "#000099",
            self.green: "#009900",
            "#000000": "#000000"  # stop backface dimming breaking
        }

        layers = int(layers)
        self.layers = layers

        self.moves = {"scramble": [], "solve": []}

        try:
            assert layers > 1
            assert isinstance(width, (int, float))

        except AssertionError:
            self.layers = layers = 2
            width = 12

        self.width = width
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
                                y_layer.append(Corner(Vector3(delta, delta, -delta), self.yellow, self.red, self.green, piece_width, 0))
                                y_layer[-1].rotate(rot_z(180))

                            elif x == layers - 1:
                                # front bottom right corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), self.yellow, self.blue, self.red, piece_width, 0))
                                y_layer[-1].rotate(rot_y(-90))
                                y_layer[-1].rotate(rot_z(180))

                            else:
                                # front bottom edges
                                y_layer.append(Edge(Vector3(d_edge - x * piece_width, delta, -delta), self.yellow, self.red, piece_width, 0))
                                y_layer[-1].rotate(rot_z(180))

                        elif y == layers - 1:
                            if x == 0:
                                # front top left corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), self.white, self.green, self.red, piece_width, 0))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # front top right corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), self.white, self.red, self.blue, piece_width, 0))

                            else:
                                # front top edges
                                y_layer.append(Edge(Vector3(x * piece_width - d_edge, delta, -delta), self.white, self.red, piece_width, 0))

                        else:
                            if x == 0:
                                # front middle left edges
                                y_layer.append(Edge(Vector3(y * piece_width - d_edge, delta, -delta), self.green, self.red, piece_width, 2))
                                y_layer[-1].rotate(rot_z(-90))

                            elif x == layers - 1:
                                # front middle right edges
                                y_layer.append(Edge(Vector3(d_edge - y * piece_width, delta, -delta), self.blue, self.red, piece_width, 2))
                                y_layer[-1].rotate(rot_z(90))

                            else:
                                # front center
                                y_layer.append(Center(Vector3(x * piece_width - d_edge, delta, y * piece_width - d_edge), self.red, piece_width))
                                y_layer[-1].rotate(rot_x(90))

                    elif z == layers - 1:
                        if y == 0:
                            if x == 0:
                                # back bottom left corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), self.yellow, self.green, self.orange, piece_width, 0))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # back bottom right corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), self.yellow, self.orange, self.blue, piece_width, 0))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(180))

                            else:
                                # back bottom edges
                                y_layer.append(Edge(Vector3(x * piece_width - d_edge, delta, -delta), self.yellow, self.orange, piece_width, 0))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(180))

                        elif y == layers - 1:
                            if x == 0:
                                # back top left corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), self.white, self.orange, self.green, piece_width, 0))
                                y_layer[-1].rotate(rot_y(180))

                            elif x == layers - 1:
                                # back top right corner
                                y_layer.append(Corner(Vector3(delta, delta, -delta), self.white, self.blue, self.orange, piece_width, 0))
                                y_layer[-1].rotate(rot_y(90))

                            else:
                                # back top edges
                                y_layer.append(Edge(Vector3(d_edge - x * piece_width, delta, -delta), self.white, self.orange, piece_width, 0))
                                y_layer[-1].rotate(rot_y(180))

                        else:
                            if x == 0:
                                # back left edges
                                y_layer.append(Edge(Vector3(d_edge - y * piece_width, delta, -delta), self.green, self.orange, piece_width, 2))
                                y_layer[-1].rotate(rot_z(90))
                                y_layer[-1].rotate(rot_y(180))

                            elif x == layers - 1:
                                # back right edges
                                y_layer.append(Edge(Vector3(y * piece_width - d_edge, delta, -delta), self.blue, self.orange, piece_width, 2))
                                y_layer[-1].rotate(rot_z(-90))
                                y_layer[-1].rotate(rot_y(180))

                            else:
                                # back center
                                y_layer.append(Center(Vector3(x * piece_width - d_edge, delta, d_edge - y * piece_width), self.orange, piece_width))
                                y_layer[-1].rotate(rot_x(-90))

                    else:
                        if y == 0:
                            if x == 0:
                                # middle bottom left edges
                                y_layer.append(Edge(Vector3(z * piece_width - d_edge, delta, -delta), self.yellow, self.green, piece_width, 0))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # middle bottom right edges
                                y_layer.append(Edge(Vector3(d_edge - z * piece_width, delta, -delta), self.yellow, self.blue, piece_width, 0))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(90))

                            else:
                                # bottom center
                                y_layer.append(Center(Vector3(d_edge - x * piece_width, delta, z * piece_width - d_edge), self.yellow, piece_width))
                                y_layer[-1].rotate(rot_z(180))

                        elif y == layers - 1:
                            if x == 0:
                                # middle top left edges
                                y_layer.append(Edge(Vector3(d_edge - z * piece_width, delta, -delta), self.white, self.green, piece_width, 0))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # middle top right edges
                                y_layer.append(Edge(Vector3(z * piece_width - d_edge, delta, -delta), self.white, self.blue, piece_width, 0))
                                y_layer[-1].rotate(rot_y(90))

                            else:
                                # top center
                                y_layer.append(Center(Vector3(x * piece_width - d_edge, delta, z * piece_width - d_edge), self.white, piece_width))

                        else:
                            if x == 0:
                                # left center
                                y_layer.append(Center(Vector3(y * piece_width - d_edge, delta, z * piece_width - d_edge), self.green, piece_width))
                                y_layer[-1].rotate(rot_z(-90))

                            elif x == layers - 1:
                                # right center
                                y_layer.append(Center(Vector3(d_edge - y * piece_width, delta, z * piece_width - d_edge), self.blue, piece_width))
                                y_layer[-1].rotate(rot_z(90))

                            else:
                                # interior pieces
                                y_layer.append(None)

                z_layer.append(y_layer)

            self.pieces.append(z_layer)

        self.display = display
        self.initial = [[[piece for piece in y] for y in z] for z in self.pieces]

        self.running = True
        self.tmp_pieces = self.pieces
        self.moving_threads = []
        threading.Thread(target=self.handle_movement).start()
        self.duration = turn_duration

    @property
    def solved(self):
        pieces = [piece for z in self.pieces for y in z for piece in y]
        initial = [piece for z in self.initial for y in z for piece in y]
        return all(map(lambda x: x[0] is x[1], zip(pieces, initial)))


    def rotate(self, move: Move) -> None:
        face = move.face + ("2" if move.turns == 2 else ("'" if move.turns == 3 else ""))
        depth = move.depth
        if depth >= self.layers:
            # if depth to large rotate the first piece
            depth = 0

        if depth == self.layers - 1:
            # rotating reverse face
            opposite = {"F": "B'", "B": "F'", "R": "L'", "L": "R'", "U": "D'", "D": "U'"}
            if face in opposite:
                face = opposite[face]
                depth = 0

        if face == "F":
            if depth == 0:
                # update corner orientation
                self.pieces[0][self.layers - 1][0].orient = (self.pieces[0][self.layers - 1][0].orient + 2) % 3
                self.pieces[0][self.layers - 1][self.layers - 1].orient = (self.pieces[0][self.layers - 1][self.layers - 1].orient + 1) % 3
                self.pieces[0][0][self.layers - 1].orient = (self.pieces[0][0][self.layers - 1].orient + 2) % 3
                self.pieces[0][0][0].orient = (self.pieces[0][0][0].orient + 1) % 3

            # update edge orientation
            for i in range(self.layers):
                for j in range(self.layers):
                    if isinstance(self.pieces[depth][i][j], Edge):
                        if depth == 0:
                            if self.pieces[depth][i][j].orient == 0:
                                self.pieces[depth][i][j].orient = 2

                            elif self.pieces[depth][i][j].orient == 2:
                                self.pieces[depth][i][j].orient = 0

                            elif self.pieces[depth][i][j].orient == 1:
                                self.pieces[depth][i][j].orient = 3

                            elif self.pieces[depth][i][j].orient == 3:
                                self.pieces[depth][i][j].orient = 1

                        else:
                            if self.pieces[depth][i][j].orient == 0:
                                self.pieces[depth][i][j].orient = 1

                            elif self.pieces[depth][i][j].orient == 1:
                                self.pieces[depth][i][j].orient = 0

            for j in range(self.layers // 2):
                # update corner positions
                tmp = self.pieces[depth][j][j]
                self.pieces[depth][j][j] = self.pieces[depth][j][self.layers - j - 1]
                self.pieces[depth][j][self.layers - j - 1] = self.pieces[depth][self.layers - j - 1][self.layers - j - 1]
                self.pieces[depth][self.layers - j - 1][self.layers - j - 1] = self.pieces[depth][self.layers - j - 1][j]
                self.pieces[depth][self.layers - j - 1][j] = tmp

                # update edge positions
                for i in range(j + 1, self.layers - j - 1):
                    tmp = self.pieces[depth][j][i]
                    self.pieces[depth][j][i] = self.pieces[depth][i][self.layers - j - 1]
                    self.pieces[depth][i][self.layers - j - 1] = self.pieces[depth][self.layers - j - 1][self.layers - i - 1]
                    self.pieces[depth][self.layers - j - 1][self.layers - i - 1] = self.pieces[depth][self.layers - i - 1][j]
                    self.pieces[depth][self.layers - i - 1][j] = tmp

        elif face == "B":
            depth = self.layers - depth - 1

            if depth == self.layers - 1:
                # update corner orientation
                self.pieces[self.layers - 1][self.layers - 1][self.layers - 1].orient = (self.pieces[self.layers - 1][self.layers - 1][self.layers - 1].orient + 2) % 3
                self.pieces[self.layers - 1][self.layers - 1][0].orient = (self.pieces[self.layers - 1][self.layers - 1][0].orient + 1) % 3
                self.pieces[self.layers - 1][0][0].orient = (self.pieces[self.layers - 1][0][0].orient + 2) % 3
                self.pieces[self.layers - 1][0][self.layers - 1].orient = (self.pieces[self.layers - 1][0][self.layers - 1].orient + 1) % 3

            # update edge orientation
            for i in range(self.layers):
                for j in range(self.layers):
                    if isinstance(self.pieces[depth][i][j], Edge):
                        if depth == self.layers - 1:
                            if self.pieces[depth][i][j].orient == 0:
                                self.pieces[depth][i][j].orient = 2

                            elif self.pieces[depth][i][j].orient == 2:
                                self.pieces[depth][i][j].orient = 0

                            elif self.pieces[depth][i][j].orient == 1:
                                self.pieces[depth][i][j].orient = 3

                            elif self.pieces[depth][i][j].orient == 3:
                                self.pieces[depth][i][j].orient = 1

                        else:
                            if self.pieces[depth][i][j].orient == 0:
                                self.pieces[depth][i][j].orient = 1

                            elif self.pieces[depth][i][j].orient == 1:
                                self.pieces[depth][i][j].orient = 0

            for j in range(self.layers // 2):
                # update corner positions
                tmp = self.pieces[depth][j][self.layers - j - 1]
                self.pieces[depth][j][self.layers - j - 1] = self.pieces[depth][j][j]
                self.pieces[depth][j][j] = self.pieces[depth][self.layers - j - 1][j]
                self.pieces[depth][self.layers - j - 1][j] = self.pieces[depth][self.layers - j - 1][self.layers - j - 1]
                self.pieces[depth][self.layers - j - 1][self.layers - j - 1] = tmp

                # update edge positions
                for i in range(j + 1, self.layers - j - 1):
                    tmp = self.pieces[depth][j][self.layers - i - 1]
                    self.pieces[depth][j][self.layers - i - 1] = self.pieces[depth][i][j]
                    self.pieces[depth][i][j] = self.pieces[depth][self.layers - j - 1][i]
                    self.pieces[depth][self.layers - j - 1][i] = self.pieces[depth][self.layers - i - 1][self.layers - j - 1]
                    self.pieces[depth][self.layers - i - 1][self.layers - j - 1] = tmp

        elif face == "R":
            depth = self.layers - depth - 1

            if depth == self.layers - 1:
                # update corner orientation
                self.pieces[0][self.layers - 1][self.layers - 1].orient = (self.pieces[0][self.layers - 1][self.layers - 1].orient + 2) % 3
                self.pieces[self.layers - 1][self.layers - 1][self.layers - 1].orient = (self.pieces[self.layers - 1][self.layers - 1][self.layers - 1].orient + 1) % 3
                self.pieces[self.layers - 1][0][self.layers - 1].orient = (self.pieces[self.layers - 1][0][self.layers - 1].orient + 2) % 3
                self.pieces[0][0][self.layers - 1].orient = (self.pieces[0][0][self.layers - 1].orient + 1) % 3

            # update edge orientation
            for i in range(self.layers):
                for j in range(self.layers):
                    if isinstance(self.pieces[i][j][depth], Edge):
                        if depth == self.layers - 1:
                            if self.pieces[i][j][depth].orient == 0:
                                self.pieces[i][j][depth].orient = 3

                            elif self.pieces[i][j][depth].orient == 3:
                                self.pieces[i][j][depth].orient = 0

                            elif self.pieces[i][j][depth].orient == 1:
                                self.pieces[i][j][depth].orient = 2

                            elif self.pieces[i][j][depth].orient == 2:
                                self.pieces[i][j][depth].orient = 1

                        else:
                            if self.pieces[i][j][depth].orient == 0:
                                self.pieces[i][j][depth].orient = 1

                            elif self.pieces[i][j][depth].orient == 1:
                                self.pieces[i][j][depth].orient = 0

            for j in range(self.layers // 2):
                # update corner positions
                tmp = self.pieces[j][j][depth]
                self.pieces[j][j][depth] = self.pieces[self.layers - j - 1][j][depth]
                self.pieces[self.layers - j - 1][j][depth] = self.pieces[self.layers - j - 1][self.layers - j - 1][depth]
                self.pieces[self.layers - j - 1][self.layers - j - 1][depth] = self.pieces[j][self.layers - j - 1][depth]
                self.pieces[j][self.layers - j - 1][depth] = tmp

                # update edge positions
                for i in range(j + 1, self.layers - j - 1):
                    tmp = self.pieces[i][j][depth]
                    self.pieces[i][j][depth] = self.pieces[self.layers - j - 1][i][depth]
                    self.pieces[self.layers - j - 1][i][depth] = self.pieces[self.layers - i - 1][self.layers - j - 1][depth]
                    self.pieces[self.layers - i - 1][self.layers - j - 1][depth] = self.pieces[j][self.layers - i - 1][depth]
                    self.pieces[j][self.layers - i - 1][depth] = tmp

        elif face == "L":
            if depth == 0:
                # update corner orientation
                self.pieces[self.layers - 1][self.layers - 1][0].orient = (self.pieces[self.layers - 1][self.layers - 1][0].orient + 2) % 3
                self.pieces[0][self.layers - 1][0].orient = (self.pieces[0][self.layers - 1][0].orient + 1) % 3
                self.pieces[0][0][0].orient = (self.pieces[0][0][0].orient + 2) % 3
                self.pieces[self.layers - 1][0][0].orient = (self.pieces[self.layers - 1][0][0].orient + 1) % 3

            # update edge orientation
            for i in range(self.layers):
                for j in range(self.layers):
                    if isinstance(self.pieces[i][j][depth], Edge):
                        if depth == 0:
                            if self.pieces[i][j][depth].orient == 0:
                                self.pieces[i][j][depth].orient = 3

                            elif self.pieces[i][j][depth].orient == 3:
                                self.pieces[i][j][depth].orient = 0

                            elif self.pieces[i][j][depth].orient == 1:
                                self.pieces[i][j][depth].orient = 2

                            elif self.pieces[i][j][depth].orient == 2:
                                self.pieces[i][j][depth].orient = 1

                        else:
                            if self.pieces[i][j][depth].orient == 0:
                                self.pieces[i][j][depth].orient = 1

                            elif self.pieces[i][j][depth].orient == 1:
                                self.pieces[i][j][depth].orient = 0

            for j in range(self.layers // 2):
                # update corner positions
                tmp = self.pieces[self.layers - j - 1][j][depth]
                self.pieces[self.layers - j - 1][j][depth] = self.pieces[j][j][depth]
                self.pieces[j][j][depth] = self.pieces[j][self.layers - j - 1][depth]
                self.pieces[j][self.layers - j - 1][depth] = self.pieces[self.layers - j - 1][self.layers - j - 1][depth]
                self.pieces[self.layers - j -1][self.layers - j - 1][depth] = tmp

                # update edge positions
                for i in range(j + 1, self.layers - j - 1):
                    tmp = self.pieces[self.layers - i - 1][j][depth]
                    self.pieces[self.layers - i - 1][j][depth] = self.pieces[j][i][depth]
                    self.pieces[j][i][depth] = self.pieces[i][self.layers - j - 1][depth]
                    self.pieces[i][self.layers - j - 1][depth] = self.pieces[self.layers - j - 1][self.layers - i - 1][depth]
                    self.pieces[self.layers - j - 1][self.layers - i - 1][depth] = tmp

        elif face == "U":
            depth = self.layers - depth - 1

            # corner orientation unchanged

            # update edge orientation
            for i in range(self.layers):
                for j in range(self.layers):
                    if depth != self.layers - 1:
                        if isinstance(self.pieces[i][depth][j], Edge):
                            if self.pieces[i][depth][j].orient == 2:
                                self.pieces[i][depth][j].orient = 3

                            elif self.pieces[i][depth][j].orient == 3:
                                self.pieces[i][depth][j].orient = 2

            for j in range(self.layers // 2):
                # update corner positions
                tmp = self.pieces[j][depth][j]
                self.pieces[j][depth][j] = self.pieces[j][depth][self.layers - j - 1]
                self.pieces[j][depth][self.layers - j - 1] = self.pieces[self.layers - j - 1][depth][self.layers - j - 1]
                self.pieces[self.layers - j - 1][depth][self.layers - j - 1] = self.pieces[self.layers - j - 1][depth][j]
                self.pieces[self.layers - j - 1][depth][j] = tmp

                # update edge positions
                for i in range(j + 1, self.layers - j - 1):
                    tmp = self.pieces[j][depth][i]
                    self.pieces[j][depth][i] = self.pieces[i][depth][self.layers - j - 1]
                    self.pieces[i][depth][self.layers - j - 1] = self.pieces[self.layers - j - 1][depth][self.layers - i - 1]
                    self.pieces[self.layers - j - 1][depth][self.layers - i - 1] = self.pieces[self.layers - i - 1][depth][j]
                    self.pieces[self.layers - i - 1][depth][j] = tmp

        elif face == "D":
            # corner orientation unchanged

            # update edge orientation
            for i in range(self.layers):
                for j in range(self.layers):
                    if depth != 0:
                        if isinstance(self.pieces[i][depth][j], Edge):
                            if self.pieces[i][depth][j].orient == 2:
                                self.pieces[i][depth][j].orient = 3

                            elif self.pieces[i][depth][j].orient == 3:
                                self.pieces[i][depth][j].orient = 2

            for j in range(self.layers // 2):
                # update corner positions
                tmp = self.pieces[self.layers - j - 1][depth][j]
                self.pieces[self.layers - j - 1][depth][j] = self.pieces[self.layers - j - 1][depth][self.layers - j - 1]
                self.pieces[self.layers - j - 1][depth][self.layers - j - 1] = self.pieces[j][depth][self.layers - j - 1]
                self.pieces[j][depth][self.layers - j - 1] = self.pieces[j][depth][j]
                self.pieces[j][depth][j] = tmp

                # update edge positions
                for i in range(j + 1, self.layers - j - 1):
                    tmp = self.pieces[self.layers - j - 1][depth][i]
                    self.pieces[self.layers - j - 1][depth][i] = self.pieces[self.layers - i - 1][depth][self.layers - j - 1]
                    self.pieces[self.layers - i - 1][depth][self.layers - j - 1] = self.pieces[j][depth][self.layers - i - 1]
                    self.pieces[j][depth][self.layers - i - 1] = self.pieces[i][depth][j]
                    self.pieces[i][depth][j] = tmp

        elif face.endswith("'"):
            # reverse patterns, anti-clockwise instead of clockwise
            [self.rotate(Move(face[:-1], 1, depth)) for _ in range(3)]

        elif face.endswith("2"):
            # 180 degree turn
            [self.rotate(Move(face[:-1], 1, depth)) for _ in range(2)]

        # get copy of pieces to allow updating future positions before the actual pieces have stopped rotating
        pieces = [[[piece for piece in y] for y in z] for z in self.pieces]

        self.moving_threads.append(threading.Thread(target=self.rotate_pieces, args=(face, depth, 3, pieces)))

    def handle_movement(self) -> None:
        while self.running:
            if self.moving_threads:
                self.moving_threads[0].start()
                self.moving_threads[0].join()
                self.moving_threads.pop(0)

            elif self.display:
                if self.solved:
                    time.sleep(6)
                    self.scramble()
                    self.moving_threads.append(threading.Thread(target=time.sleep, args=(6,)))
                    self.solve()

    def rotate_pieces(self, face: str, depth: int, steps: int, pieces: list) -> None:
        # rotate pieces in scene
        if self.duration == 0:
            steps = 1

        angle = 90/steps
        for _ in range(steps):
            if face == "F":
                [pieces[depth][i][j].rotate(rot_z(angle)) for i in range(self.layers) for j in range(self.layers) if pieces[depth][i][j] is not None]

            elif face == "B":
                [pieces[depth][i][j].rotate(rot_z(-angle)) for i in range(self.layers) for j in range(self.layers) if pieces[depth][i][j] is not None]

            elif face == "R":
                [pieces[i][j][depth].rotate(rot_x(-angle)) for i in range(self.layers) for j in range(self.layers) if pieces[i][j][depth] is not None]

            elif face == "L":
                [pieces[i][j][depth].rotate(rot_x(angle)) for i in range(self.layers) for j in range(self.layers) if pieces[i][j][depth] is not None]

            elif face == "U":
                [pieces[i][depth][j].rotate(rot_y(-angle)) for i in range(self.layers) for j in range(self.layers) if pieces[i][depth][j] is not None]

            elif face == "D":
                [pieces[i][depth][j].rotate(rot_y(angle)) for i in range(self.layers) for j in range(self.layers) if pieces[i][depth][j] is not None]

            self.tmp_pieces = [[[piece.copy() if piece is not None else None for piece in y] for y in z] for z in pieces]

            time.sleep(self.duration / steps / 1000)

    def scramble(self) -> None:
        random.seed(time.time())
        for i in range(10 * self.layers):
            face = random.choice(["F", "B", "R", "L", "U", "D"])
            turns = random.randint(1, 3)
            depth = random.randint(0, self.layers - 1)
            move = Move(face, turns, depth)
            self.moves["scramble"].append(move)
            self.rotate(move)

    def save_state(self, global_rotation: Matrix3x3) -> str:
        state = str(self.width) + ":" + str(self.layers) + ":"
        state += ",".join(str(x) for y in global_rotation.data for x in y) + ":"
        return state + ",".join(map(str, self.moves["scramble"])) + ":" + ",".join(map(str, self.moves["solve"]))

    @classmethod
    def load_state(cls, state: str) -> tuple:
        state = state.split(":")
        obj = cls(int(state[0]), int(state[1]))
        rotation = [float(i) for i in state[2].split(",")]
        scramble = [i for i in state[3].split(",") if i.strip()]
        moves = [i for i in state[4].split(",") if i.strip()]
        for move in scramble:
            face = move[0]
            turns = int(move[1])
            new_move = Move(face, turns)
            if len(move) > 2:
                new_move.depth = int(move[2:])

            obj.rotate(new_move)

        for move in moves:
            face = move[0]
            turns = int(move[1])
            new_move = Move(face, turns)
            if len(move) > 2:
                new_move.depth = int(move[2:])

            obj.rotate(new_move)

        return obj, Matrix3x3([rotation[:3], rotation[3:6], rotation[6:]])

    def solve(self):
        if self.layers == 2:
            # 2x2 cube

            def drop_y(x, z):
                # move piece downwards whilst maintaining x and z positions and without moving other top pieces
                if x == 0:
                    if z == 0:
                        self.evaluate("L D' L'")

                    else:
                        self.evaluate("L' D L")

                else:
                    if z == 0:
                        self.evaluate("R' D R")

                    else:
                        self.evaluate("R D' R'")

            # front top left
            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if piece.col1 == self.white and piece.col2 == self.green and piece.col3 == self.red:
                            if y == 1:
                                drop_y(x, z)

                            if x == 1:
                                if z == 0:
                                    self.rotate(Move("D", 3))

                                else:
                                    self.rotate(Move("D", 2))

                            elif z == 1:
                                self.rotate(Move("D"))

                            self.evaluate("L D L'")

            # front top right
            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if piece.col1 == self.white and piece.col2 == self.red and piece.col3 == self.blue:
                            if y == 1:
                                drop_y(x, z)

                            if x == 0:
                                if z == 0:
                                    self.rotate(Move("D"))

                                else:
                                    self.rotate(Move("D", 2))

                            elif z == 1:
                                self.rotate(Move("D", 3))

                            self.evaluate("R' D' R")

            # back top left
            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if piece.col1 == self.white and piece.col2 == self.orange and piece.col3 == self.green:
                            if y == 1:
                                drop_y(x, z)

                            if x == 1:
                                if z == 0:
                                    self.rotate(Move("D", 2))

                                else:
                                    self.rotate(Move("D"))

                            elif z == 0:
                                self.rotate(Move("D", 3))

                            self.evaluate("L' D' L")

            # back top right
            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if piece.col1 == self.white and piece.col2 == self.blue and piece.col3 == self.orange:
                            if y == 1:
                                drop_y(x, z)

                            if x == 0:
                                if z == 0:
                                    self.rotate(Move("D", 2))

                                else:
                                    self.rotate(Move("D", 3))

                            elif z == 0:
                                self.rotate(Move("D"))

                            self.evaluate("R D R'")

            # rotate top corners correctly
            if self.pieces[0][1][0].orient == 1:
                self.evaluate("L D L' D' L D L'")

            elif self.pieces[0][1][0].orient == 2:
                self.evaluate("L D' L' D L D' L'")

            if self.pieces[0][1][1].orient == 1:
                self.evaluate("F D F' D' F D F'")

            elif self.pieces[0][1][1].orient == 2:
                self.evaluate("F D' F' D F D' F'")

            if self.pieces[1][1][0].orient == 1:
                self.evaluate("B D B' D' B D B'")

            elif self.pieces[1][1][0].orient == 2:
                self.evaluate("B D' B' D B D' B'")

            if self.pieces[1][1][1].orient == 1:
                self.evaluate("R D R' D' R D R'")

            elif self.pieces[1][1][1].orient == 2:
                self.evaluate("R D' R' D R D' R'")

            # front bottom left
            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if piece.col1 == self.yellow and piece.col2 == self.red and piece.col3 == self.green:
                            if z == 1:
                                if x == 0:
                                    self.rotate(Move("D"))

                                else:
                                    self.rotate(Move("D", 2))

                            elif x == 1:
                                self.rotate(Move("D", 3))

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if piece.col1 == self.yellow and piece.col2 == self.blue and piece.col3 == self.red:
                            if z == 1:
                                self.evaluate("R' D L D' R D L' D'")
                                if x == 1:
                                    self.evaluate("R' D L D' R D L' D'")

            if not ((piece := self.pieces[1][0][0]).col1 == self.yellow and piece.col2 == self.green and piece.col3 == self.orange):
                # back bottom left and back bottom right need to be swapped
                self.evaluate("L' D R D' L D R' D' L' D R D' L D R'")

            for _ in range(4):
                self.rotate(Move("D"))

                if self.pieces[0][0][0].orient == 1:
                    if self.pieces[0][0][1].orient == 2:
                        self.evaluate("L' U L U' L' U L D' L' U' L U L' U' L D")

                    elif self.pieces[1][0][0].orient == 2:
                        self.evaluate("L' U L U' L' U L D L' U' L U L' U' L D'")

                    elif self.pieces[1][0][1].orient == 2:
                        self.evaluate("L' U L U' L' U L D2 L' U' L U L' U' L D2")

                    elif self.pieces[0][0][1].orient == 0:
                        self.evaluate("L' U L U' L' U L D L' U' L U L' U2 L U L' U' L D L' U L U' L' U L D2")

                    elif self.pieces[1][0][0].orient == 0:
                        self.evaluate("L' U L U' L' U L D' L' U' L U L' U2 L U L' U' L D' L' U L U' L' U L D2")

                    elif self.pieces[1][0][1].orient == 0:
                        self.evaluate("D' L' U L U' L' U L D L' U' L U L' U2 L U L' U' L D L' U L U' L' U L D'")

                if self.pieces[0][0][0].orient == 2:
                    if self.pieces[0][0][1].orient == 1:
                        self.evaluate("L' U' L U L' U' L D' L' U L U' L' U L D")

                    elif self.pieces[1][0][0].orient == 1:
                        self.evaluate("L' U' L U L' U' L D L' U L U' L' U L D'")

                    elif self.pieces[1][0][1].orient == 1:
                        self.evaluate("L' U' L U L' U' L D2 L' U L U' L' U L D2")

                    elif self.pieces[0][0][1].orient == 0:
                        self.evaluate("L' U' L U L' U' L D L' U L U' L' U2 L U' L' U L D L' U' L U L' U' L D2")

                    elif self.pieces[1][0][0].orient == 0:
                        self.evaluate("L' U' L U L' U' L D' L' U L U' L' U2 L U' L' U L D' L' U' L U L' U' L D2")

                    elif self.pieces[1][0][1].orient == 0:
                        self.evaluate("D' L' U' L U L' U' L D L' U L U' L' U2 L U' L' U L D L' U' L U L' U' L D'")

        elif self.layers == 3:
            # 3x3 cube

            # re-orient centers
            # centers cannot turn relatively, aligning two aligns them all
            if self.pieces[1][2][1].col != self.white:
                if self.pieces[0][1][1].col == self.white:
                    self.rotate(Move("R", 1, 1))

                elif self.pieces[2][1][1].col == self.white:
                    self.rotate(Move("L", 1, 1))

                elif self.pieces[1][1][0].col == self.white:
                    self.rotate(Move("F", 1, 1))

                elif self.pieces[1][1][2].col == self.white:
                    self.rotate(Move("B", 1, 1))

                else:
                    self.rotate(Move("F", 2, 1))

            if self.pieces[0][1][1].col != self.red:
                if self.pieces[1][1][2].col == self.red:
                    self.rotate(Move("U", 1, 1))

                elif self.pieces[1][1][0].col == self.red:
                    self.rotate(Move("D", 1, 1))

                else:
                    self.rotate(Move("U", 2, 1))

            # construct white cross
            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Edge) and piece.col1 == self.white and piece.col2 == self.red:
                            if y == 2:
                                if x == 0:
                                    self.rotate(Move("U", 3))

                                elif x == 2:
                                    self.rotate(Move("U"))

                                elif z == 2:
                                    self.rotate(Move("U", 2))

                            elif y == 0:
                                if x == 0:
                                    self.evaluate("L2 U'")

                                elif x == 2:
                                    self.evaluate("R2 U")

                                elif z == 0:
                                    self.evaluate("F2")

                                elif z == 2:
                                    self.evaluate("B2 U2")

                            else:
                                if z == 0:
                                    if x == 0:
                                        self.rotate(Move("F"))

                                    else:
                                        self.rotate(Move("F", 3))

                                else:
                                    if x == 0:
                                        self.evaluate("B' U2")

                                    else:
                                        self.evaluate("B U2")

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Edge) and piece.col1 == self.white and piece.col2 == self.green:
                            if y == 2:
                                if x == 2:
                                    self.evaluate("F U2 F'")

                                elif z == 2:
                                    self.evaluate("F U' F'")

                            elif y == 0:
                                if x == 0:
                                    self.rotate(Move("L", 2))

                                elif x == 2:
                                    self.evaluate("D2 L2")

                                elif z == 0:
                                    self.evaluate("D' L2")

                                elif z == 2:
                                    self.evaluate("D L2")

                            else:
                                if z == 0:
                                    if x == 0:
                                        self.rotate(Move("L", 3))

                                    else:
                                        self.evaluate("U' F' U")

                                else:
                                    if x == 0:
                                        self.rotate(Move("L"))

                                    else:
                                        self.evaluate("U2 R' U2")

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Edge) and piece.col1 == self.white and piece.col2 == self.blue:
                            if y == 2:
                                if z == 2:
                                    self.evaluate("B' R'")

                            elif y == 0:
                                if x == 0:
                                    self.evaluate("D2 R2")

                                elif x == 2:
                                    self.rotate(Move("R", 2))

                                elif z == 0:
                                    self.evaluate("D R2")

                                elif z == 2:
                                    self.evaluate("D' R2")

                            else:
                                if z == 0:
                                    if x == 0:
                                        self.evaluate("L D2 R2 L'")

                                    else:
                                        self.rotate(Move("R"))

                                else:
                                    if x == 0:
                                        self.evaluate("B2 R'")

                                    else:
                                        self.rotate(Move("R", 3))

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Edge):
                            if piece.col1 == self.white and piece.col2 == self.orange:
                                if y == 0:
                                    if x == 0:
                                        self.evaluate("D' B2")

                                    elif x == 2:
                                        self.evaluate("D B2")

                                    elif z == 0:
                                        self.evaluate("D2 B2")

                                    elif z == 2:
                                        self.rotate(Move("B", 2))

                                elif y == 1:
                                    if z == 0:
                                        if x == 0:
                                            self.evaluate("L D' B2 L'")

                                        else:
                                            self.evaluate("R' D B2 R")

                                    else:
                                        if x == 0:
                                            self.rotate(Move("B", 3))

                                        else:
                                            self.rotate(Move("B"))

            # rotate top edges correctly
            if self.pieces[0][2][1].orient == 1:
                self.evaluate("F R' D' R F2")

            if self.pieces[1][2][0].orient == 1:
                self.evaluate("L F' D' F L2")

            if self.pieces[1][2][2].orient == 1:
                self.evaluate("R B' D' B R2")

            if self.pieces[2][2][1].orient == 1:
                self.evaluate("B L' D' L B2")

            # complete white corners
            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Corner) and piece.col1 == self.white and piece.col3 == self.red:
                            if y == 2:
                                if z == 0 and x == 2:
                                    self.evaluate("R' L D' R L'")

                                elif z == 2:
                                    if x == 0:
                                        self.evaluate("B F' D B' F")

                                    else:
                                        self.evaluate("B' L D2 B L'")

                            else:
                                if z == 0:
                                    if x == 0:
                                        self.evaluate("L D L'")

                                    else:
                                        self.evaluate("D' L D L'")

                                elif x == 0:
                                    self.evaluate("D L D L'")

                                else:
                                    self.evaluate("D2 L D L'")

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Corner) and piece.col1 == self.white and piece.col2 == self.red:
                            if y == 2 and z == 2:
                                if x == 0:
                                    self.evaluate("B R' D2 B' R")

                                else:
                                    self.evaluate("B' F D' B F'")

                            elif y == 0:
                                if z == 0:
                                    if x == 0:
                                        self.evaluate("R' D R")

                                    else:
                                        self.evaluate("R' D' R")

                                elif x == 0:
                                    self.evaluate("D2 R' D' R")

                                else:
                                    self.evaluate("D' R' D' R")

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Corner) and piece.col1 == self.white and piece.col3 == self.green:
                            if y == 2 and z == 2 and x == 2:
                                self.evaluate("B' L' D L2 B L'")

                            elif y == 0:
                                if z == 0:
                                    if x == 0:
                                        self.evaluate("D' B D B'")

                                    else:
                                        self.evaluate("D2 B D B'")

                                elif x == 0:
                                    self.evaluate("B D B'")

                                else:
                                    self.evaluate("D B D B'")

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Corner) and piece.col1 == self.white and piece.col2 == self.blue:
                            if y == 0:
                                if z == 0:
                                    if x == 0:
                                        self.evaluate("D2 R D R'")

                                    else:
                                        self.evaluate("D R D R'")

                                elif x == 0:
                                    self.evaluate("D' R D R'")

                                else:
                                    self.evaluate("R D R'")

            # rotate top corners correctly
            if self.pieces[0][2][0].orient == 1:
                self.evaluate("L D L' D' L D L'")

            if self.pieces[0][2][0].orient == 2:
                self.evaluate("L D' L' D L D' L'")

            if self.pieces[0][2][2].orient == 1:
                self.evaluate("F D F' D' F D F'")

            if self.pieces[0][2][2].orient == 2:
                self.evaluate("F D' F' D F D' F'")

            if self.pieces[2][2][0].orient == 1:
                self.evaluate("B D B' D' B D B'")

            if self.pieces[2][2][0].orient == 2:
                self.evaluate("B D' B' D B D' B'")

            if self.pieces[2][2][2].orient == 1:
                self.evaluate("R D R' D' R D R'")

            if self.pieces[2][2][2].orient == 2:
                self.evaluate("R D' R' D R D' R'")

            # complete middle edges
            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Edge) and piece.col1 == self.green and piece.col2 == self.red:
                            if y == 0:
                                if z == 0:
                                    if piece.orient == 0:
                                        self.evaluate("D L D' L' D' F' D F")

                                    else:
                                        self.evaluate("D2 F' D F D L D' L'")

                                elif z == 2:
                                    if piece.orient == 0:
                                        self.evaluate("D' L D' L' D' F' D F")

                                    else:
                                        self.evaluate("F' D F D L D' L'")

                                elif x == 0:
                                    if piece.orient == 0:
                                        self.evaluate("D2 L D' L' D' F' D F")

                                    else:
                                        self.evaluate("D' F' D F D L D' L'")

                                else:
                                    if piece.orient == 0:
                                        self.evaluate("L D' L' D' F' D F")

                                    else:
                                        self.evaluate("D F' D F D L D' L'")

                            else:
                                if z == 0:
                                    if x == 0 and piece.orient == 3:
                                        self.evaluate("L D' L' D' F' D F D' L D' L' D' F' D F")

                                    elif x == 2:
                                        if piece.orient == 2:
                                            self.evaluate("F D' F' D' R' D R D2 L D' L' D' F' D F")

                                        else:
                                            self.evaluate("F D' F' D' R' D R D' F' D F D L D' L'")

                                elif x == 0:
                                    if piece.orient == 2:
                                        self.evaluate("B D' B' D' L' D L2 D' L' D' F' D F")

                                    else:
                                        self.evaluate("B D' B' D' L' D L D F' D F D L D' L'")

                                else:
                                    if piece.orient == 2:
                                        self.evaluate("R D' R' D' B' D B D2 F' D F D L D' L'")

                                    else:
                                        self.evaluate("R D' R' D' B' D B D L D' L' D' F' D F")

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Edge) and piece.col1 == self.blue and piece.col2 == self.red:
                            if y == 0:
                                if z == 0:
                                    if piece.orient == 0:
                                        self.evaluate("D' R' D R D F D' F'")

                                    else:
                                        self.evaluate("D2 F D' F' D' R' D R")

                                elif z == 2:
                                    if piece.orient == 0:
                                        self.evaluate("D R' D R D F D' F'")

                                    else:
                                        self.evaluate("F D' F' D' R' D R")

                                elif x == 0:
                                    if piece.orient == 0:
                                        self.evaluate("R' D R D F D' F'")

                                    else:
                                        self.evaluate("D' F D' F' D' R' D R")

                                else:
                                    if piece.orient == 0:
                                        self.evaluate("D2 R' D R D F D' F'")

                                    else:
                                        self.evaluate("D F D' F' D' R' D R")

                            else:
                                if z == 0 and x == 2 and piece.orient == 3:
                                    self.evaluate("F D' F' D' R' D R D' F D' F' D' R' D R")

                                elif z == 2:
                                    if x == 0:
                                        if piece.orient == 2:
                                            self.evaluate("B D' B' D' L' D L D2 R' D R D F D' F'")

                                        else:
                                            self.evaluate("B D' B' D' L' D L D F D' F' D' R' D R")

                                    elif piece.orient == 2:
                                        self.evaluate("R D' R' D' B' D B D2 F D' F' D' R' D R")

                                    else:
                                        self.evaluate("R D' R' D' B' D B D' R' D R D F D' F'")

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Edge) and piece.col1 == self.green and piece.col2 == self.orange:
                            if y == 0:
                                if z == 0:
                                    if piece.orient == 0:
                                        self.evaluate("D L' D L D B D' B'")

                                    else:
                                        self.evaluate("B D' B' D' L' D L")

                                elif z == 2:
                                    if piece.orient == 0:
                                        self.evaluate("D' L' D L D B D' B'")

                                    else:
                                        self.evaluate("D2 B D' B' D' L' D L")

                                elif x == 0:
                                    if piece.orient == 0:
                                        self.evaluate("D2 L' D L D B D' B'")

                                    else:
                                        self.evaluate("D B D' B' D' L' D L")

                                elif piece.orient == 0:
                                    self.evaluate("L' D L D B D' B'")

                                else:
                                    self.evaluate("D' B D' B' D' L' D L")

                            else:
                                if x == 0 and piece.orient == 3:
                                    self.evaluate("B D' B' D' L' D L D' B D' B' D' L' D L")

                                elif x == 2:
                                    if piece.orient == 2:
                                        self.evaluate("R D' R' D' B' D B B D' B' D' L' D L")

                                    else:
                                        self.evaluate("R D' R' D' B' D B D L' D L D B D' B'")

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if isinstance(piece, Edge) and piece.col1 == self.blue and piece.col2 == self.orange:
                            if y == 0:
                                if z == 0:
                                    if piece.orient == 0:
                                        self.evaluate("D' R D' R' D' B' D B")

                                    else:
                                        self.evaluate("B' D B D R D' R'")

                                elif z == 2:
                                    if piece.orient == 0:
                                        self.evaluate("D R D' R' D' B' D B")

                                    else:
                                        self.evaluate("D2 B' D B D R D' R'")

                                elif x == 0:
                                    if piece.orient == 0:
                                        self.evaluate("R D' R' D' B' D B")

                                    else:
                                        self.evaluate("D B' D B D R D' R'")

                                elif piece.orient == 0:
                                    self.evaluate("D2 R D' R' D' B' D B")

                                else:
                                    self.evaluate("D' B' D B D R D' R'")

                            elif piece.orient == 3:
                                self.evaluate("R D' R' D' B' D B D' R D' R' D' B' D B")


            # align bottom edges
            if self.pieces[2][0][1].col2 == self.red:
                self.evaluate("D2")

            elif self.pieces[1][0][0].col2 == self.red:
                self.evaluate("D")

            elif self.pieces[1][0][2].col2 == self.red:
                self.evaluate("D'")

            if self.pieces[2][0][1].col2 == self.green:
                self.evaluate("B D2 B' D' B D' B' D'")

            elif self.pieces[1][0][2].col2 == self.green:
                self.evaluate("F D2 F' D' F D' F' D2")

            if self.pieces[2][0][1].col2 == self.blue:
                self.evaluate("R D2 R' D' R D' R' D'")

            # rotate bottom edges properly
            if self.pieces[0][0][1].orient == 1:
                if self.pieces[1][0][0].orient == 1:
                    self.evaluate("L R' F L' R U' L R' F2 L' R D L R' F2 L' R U L R' F' L' R D'")

                elif self.pieces[1][0][2].orient == 1:
                    self.evaluate("L R' F L' R U' L R' F2 L' R D' L R' F2 L' R U L R' F' L' R D")

                elif self.pieces[2][0][1].orient == 1:
                    self.evaluate("L R' F L' R U' L R' F2 L' R D2 L R' F2 L' R U L R' F' L' R D2")

            if self.pieces[1][0][0].orient == 1:
                if self.pieces[1][0][2].orient == 1:
                    self.evaluate("D L R' F L' R U' L R' F2 L' R D2 L R' F2 L' R U L R' F' L' R D")

                elif self.pieces[2][0][1].orient == 1:
                    self.evaluate("D L R' F L' R U' L R' F2 L' R D L R' F2 L' R U L R' F' L' R D2")

            if self.pieces[2][0][1].orient == 1:
                self.evaluate("D2 L R' F L' R U' L R' F2 L' R D L R' F2 L' R U L R' F' L' R D")

            # align bottom corners
            if not (self.pieces[0][0][0].col2 == self.red or self.pieces[0][0][2].col2 == self.blue or self.pieces[2][0][2].col2 == self.orange or self.pieces[2][0][0].col2 == self.green):
                # no corners in correct positions
                if self.pieces[2][0][0].col2 == self.red:
                    self.evaluate("R' D L D' R D L' D'")

                elif self.pieces[2][0][2].col2 == self.red:
                    self.evaluate("R' D L D' R D L' D' R' D L D' R D L' D'")

                else:
                    self.evaluate("D L D' R' D L' D' R")

            if self.pieces[0][0][0].col2 == self.red:
                if self.pieces[2][0][0].col2 == self.blue:
                    self.evaluate("R' D L D' R D L' D'")

                elif self.pieces[0][0][2].col2 == self.green:
                    self.evaluate("D L D' R' D L' D' R")

            elif self.pieces[0][0][2].col2 == self.blue:
                if self.pieces[0][0][0].col2 == self.orange:
                    self.evaluate("B' D F D' B D F' D'")

                elif self.pieces[0][0][0].col2 == self.green:
                    self.evaluate("D F D' B' D F' D' B")

            elif self.pieces[2][0][2].col2 == self.orange:
                if self.pieces[0][0][2].col2 == self.green:
                    self.evaluate("L' D R D' L D R' D'")

                elif self.pieces[2][0][0].col2 == self.blue:
                    self.evaluate("D R D' L' D R' D' L")

            elif self.pieces[2][0][0].col2 == self.green:
                if self.pieces[2][0][2].col2 == self.red:
                    self.evaluate("F' D B D' F D B' D'")

                elif self.pieces[0][0][0].col2 == self.orange:
                    self.evaluate("D B D' F' D B' D' F")

            for _ in range(4):
                self.rotate(Move("D"))

                if self.pieces[0][0][0].orient == 1:
                    if self.pieces[0][0][2].orient == 2:
                        self.evaluate("L' U L U' L' U L D' L' U' L U L' U' L D")

                    elif self.pieces[2][0][0].orient == 2:
                        self.evaluate("L' U L U' L' U L D L' U' L U L' U' L D'")

                    elif self.pieces[2][0][2].orient == 2:
                        self.evaluate("L' U L U' L' U L D2 L' U' L U L' U' L D2")

                    elif self.pieces[0][0][2].orient == 0:
                        self.evaluate("L' U L U' L' U L D L' U' L U L' U2 L U L' U' L D L' U L U' L' U L D2")

                    elif self.pieces[2][0][0].orient == 0:
                        self.evaluate("L' U L U' L' U L D' L' U' L U L' U2 L U L' U' L D' L' U L U' L' U L D2")

                    elif self.pieces[2][0][2].orient == 0:
                        self.evaluate("D' L' U L U' L' U L D L' U' L U L' U2 L U L' U' L D L' U L U' L' U L D'")

                if self.pieces[0][0][0].orient == 2:
                    if self.pieces[0][0][2].orient == 1:
                        self.evaluate("L' U' L U L' U' L D' L' U L U' L' U L D")

                    elif self.pieces[2][0][0].orient == 1:
                        self.evaluate("L' U' L U L' U' L D L' U L U' L' U L D'")

                    elif self.pieces[2][0][2].orient == 1:
                        self.evaluate("L' U' L U L' U' L D2 L' U L U' L' U L D2")

                    elif self.pieces[0][0][2].orient == 0:
                        self.evaluate("L' U' L U L' U' L D L' U L U' L' U2 L U' L' U L D L' U' L U L' U' L D2")

                    elif self.pieces[2][0][0].orient == 0:
                        self.evaluate("L' U' L U L' U' L D' L' U L U' L' U2 L U' L' U L D' L' U' L U L' U' L D2")

                    elif self.pieces[2][0][2].orient == 0:
                        self.evaluate("D' L' U' L U L' U' L D L' U L U' L' U2 L U' L' U L D L' U' L U L' U' L D'")

    def evaluate(self, sequence: str):
        str_moves = sequence.upper().split(" ")
        moves = []
        for move in str_moves:
            if move in ["F", "B", "R", "L", "U", "D"]:
                moves.append(Move(move))

            elif move.endswith("'") and move[:-1] in ["F", "B", "R", "L", "U", "D"]:
                moves.append(Move(move[:-1], 3))

            elif move.endswith("2") and move[:-1] in ["F", "B", "R", "L", "U", "D"]:
                moves.append(Move(move[:-1], 2))

            # quietly discard invalid moves

        for move in moves:
            self.rotate(move)
