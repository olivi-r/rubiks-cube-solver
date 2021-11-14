from math3d import Matrix3x3, Mesh, Polygon, Triangle, Vector3, rot_x, rot_y, rot_z
import random, re, time

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
    def __init__(self, pos: Vector3, col1: str, col2: str, width: float):
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

    def copy(self) -> object:
        new = self.__class__(self.pos, self.col1, self.col2, self.width)
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
    def __init__(self, width: float, layers: int):
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
            self.green: "#009900"
        }

        layers = int(layers)
        self.layers = layers

        self.moves = {"scramble": [], "solve": []}

        try:
            assert layers > 1
            assert isinstance(width, (int, float))

        except AssertionError:
            layers = 2
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
                                y_layer.append(Edge(Vector3(d_edge - x * piece_width, delta, -delta), self.yellow, self.red, piece_width))
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
                                y_layer.append(Edge(Vector3(x * piece_width - d_edge, delta, -delta), self.white, self.red, piece_width))

                        else:
                            if x == 0:
                                # front middle left edges
                                y_layer.append(Edge(Vector3(y * piece_width - d_edge, delta, -delta), self.green, self.red, piece_width))
                                y_layer[-1].rotate(rot_z(-90))

                            elif x == layers - 1:
                                # front middle right edges
                                y_layer.append(Edge(Vector3(d_edge - y * piece_width, delta, -delta), self.blue, self.red, piece_width))
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
                                y_layer.append(Edge(Vector3(x * piece_width - d_edge, delta, -delta), self.yellow, self.orange, piece_width))
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
                                y_layer.append(Edge(Vector3(d_edge - x * piece_width, delta, -delta), self.white, self.orange, piece_width))
                                y_layer[-1].rotate(rot_y(180))

                        else:
                            if x == 0:
                                # back left edges
                                y_layer.append(Edge(Vector3(d_edge - y * piece_width, delta, -delta), self.green, self.orange, piece_width))
                                y_layer[-1].rotate(rot_z(90))
                                y_layer[-1].rotate(rot_y(180))

                            elif x == layers - 1:
                                # back right edges
                                y_layer.append(Edge(Vector3(y * piece_width - d_edge, delta, -delta), self.blue, self.orange, piece_width))
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
                                y_layer.append(Edge(Vector3(z * piece_width - d_edge, delta, -delta), self.yellow, self.green, piece_width))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # middle bottom right edges
                                y_layer.append(Edge(Vector3(d_edge - z * piece_width, delta, -delta), self.yellow, self.blue, piece_width))
                                y_layer[-1].rotate(rot_z(180))
                                y_layer[-1].rotate(rot_y(90))

                            else:
                                # bottom center
                                y_layer.append(Center(Vector3(d_edge - x * piece_width, delta, z * piece_width - d_edge), self.yellow, piece_width))
                                y_layer[-1].rotate(rot_z(180))

                        elif y == layers - 1:
                            if x == 0:
                                # middle top left edges
                                y_layer.append(Edge(Vector3(d_edge - z * piece_width, delta, -delta), self.white, self.green, piece_width))
                                y_layer[-1].rotate(rot_y(-90))

                            elif x == layers - 1:
                                # middle top right edges
                                y_layer.append(Edge(Vector3(z * piece_width - d_edge, delta, -delta), self.white, self.blue, piece_width))
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
            # rotate pieces in scene
            [self.pieces[depth][i][j].rotate(rot_z(90)) for i in range(self.layers) for j in range(self.layers) if self.pieces[depth][i][j] is not None]

            if depth == 0:
                # update corner orientation
                self.pieces[0][self.layers - 1][0].orient = (self.pieces[0][self.layers - 1][0].orient + 2) % 3
                self.pieces[0][self.layers - 1][self.layers - 1].orient = (self.pieces[0][self.layers - 1][self.layers - 1].orient + 1) % 3
                self.pieces[0][0][self.layers - 1].orient = (self.pieces[0][0][self.layers - 1].orient + 2) % 3
                self.pieces[0][0][0].orient = (self.pieces[0][0][0].orient + 1) % 3

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
            # rotate pieces in scene
            [self.pieces[depth][i][j].rotate(rot_z(-90)) for i in range(self.layers) for j in range(self.layers) if self.pieces[depth][i][j] is not None]

            if depth == self.layers - 1:
                # update corner orientation
                self.pieces[self.layers - 1][self.layers - 1][self.layers - 1].orient = (self.pieces[self.layers - 1][self.layers - 1][self.layers - 1].orient + 2) % 3
                self.pieces[self.layers - 1][self.layers - 1][0].orient = (self.pieces[self.layers - 1][self.layers - 1][0].orient + 1) % 3
                self.pieces[self.layers - 1][0][0].orient = (self.pieces[self.layers - 1][0][0].orient + 2) % 3
                self.pieces[self.layers - 1][0][self.layers - 1].orient = (self.pieces[self.layers - 1][0][self.layers - 1].orient + 1) % 3

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
            # rotate pieces in scene
            [self.pieces[i][j][depth].rotate(rot_x(-90)) for i in range(self.layers) for j in range(self.layers) if self.pieces[i][j][depth] is not None]

            if depth == self.layers - 1:
                # update corner orientation
                self.pieces[0][self.layers - 1][self.layers - 1].orient = (self.pieces[0][self.layers - 1][self.layers - 1].orient + 2) % 3
                self.pieces[self.layers - 1][self.layers - 1][self.layers - 1].orient = (self.pieces[self.layers - 1][self.layers - 1][self.layers - 1].orient + 1) % 3
                self.pieces[self.layers - 1][0][self.layers - 1].orient = (self.pieces[self.layers - 1][0][self.layers - 1].orient + 2) % 3
                self.pieces[0][0][self.layers - 1].orient = (self.pieces[0][0][self.layers - 1].orient + 1) % 3

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
            # rotate pieces in scene
            [self.pieces[i][j][depth].rotate(rot_x(90)) for i in range(self.layers) for j in range(self.layers) if self.pieces[i][j][depth] is not None]

            if depth == 0:
                # update corner orientation
                self.pieces[self.layers - 1][self.layers - 1][0].orient = (self.pieces[self.layers - 1][self.layers - 1][0].orient + 2) % 3
                self.pieces[0][self.layers - 1][0].orient = (self.pieces[0][self.layers - 1][0].orient + 1) % 3
                self.pieces[0][0][0].orient = (self.pieces[0][0][0].orient + 2) % 3
                self.pieces[self.layers - 1][0][0].orient = (self.pieces[self.layers - 1][0][0].orient + 1) % 3

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
            # rotate pieces in scene
            [self.pieces[i][depth][j].rotate(rot_y(-90)) for i in range(self.layers) for j in range(self.layers) if self.pieces[i][depth][j] is not None]

            # corner orientations unchanged

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
            # rotate pieces in scene
            [self.pieces[i][depth][j].rotate(rot_y(90)) for i in range(self.layers) for j in range(self.layers) if self.pieces[i][depth][j] is not None]

            # corner orientation unchanged

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

    def solve(self):
        if self.layers == 2:
            # 2x2 cube

            def drop_y(x, z):
                # move piece downwards whilst maintaining x and z positions and without moving other top pieces
                if x == 0:
                    if z == 0:
                        self.rotate(Move("L"))
                        self.rotate(Move("D", 3))
                        self.rotate(Move("L", 3))

                    else:
                        self.rotate(Move("L", 3))
                        self.rotate(Move("D"))
                        self.rotate(Move("L"))

                else:
                    if z == 0:
                        self.rotate(Move("R", 3))
                        self.rotate(Move("D"))
                        self.rotate(Move("R"))

                    else:
                        self.rotate(Move("R"))
                        self.rotate(Move("D", 3))
                        self.rotate(Move("R", 3))

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

                            self.rotate(Move("L"))
                            self.rotate(Move("D"))
                            self.rotate(Move("L", 3))

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

                            self.rotate(Move("R", 3))
                            self.rotate(Move("D", 3))
                            self.rotate(Move("R"))

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

                            self.rotate(Move("L", 3))
                            self.rotate(Move("D", 3))
                            self.rotate(Move("L"))

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

                            self.rotate(Move("R"))
                            self.rotate(Move("D"))
                            self.rotate(Move("R", 3))

            # rotate top corners correctly
            if self.pieces[0][1][0].orient == 1:
                self.rotate(Move("L"))
                self.rotate(Move("D"))
                self.rotate(Move("L", 3))
                self.rotate(Move("D", 3))
                self.rotate(Move("L"))
                self.rotate(Move("D"))
                self.rotate(Move("L", 3))

            elif self.pieces[0][1][0].orient == 2:
                self.rotate(Move("L"))
                self.rotate(Move("D", 3))
                self.rotate(Move("L", 3))
                self.rotate(Move("D"))
                self.rotate(Move("L"))
                self.rotate(Move("D", 3))
                self.rotate(Move("L", 3))

            if self.pieces[0][1][1].orient == 1:
                self.rotate(Move("F"))
                self.rotate(Move("D"))
                self.rotate(Move("F", 3))
                self.rotate(Move("D", 3))
                self.rotate(Move("F"))
                self.rotate(Move("D"))
                self.rotate(Move("F", 3))

            elif self.pieces[0][1][1].orient == 2:
                self.rotate(Move("F"))
                self.rotate(Move("D", 3))
                self.rotate(Move("F", 3))
                self.rotate(Move("D"))
                self.rotate(Move("F"))
                self.rotate(Move("D", 3))
                self.rotate(Move("F", 3))

            if self.pieces[1][1][0].orient == 1:
                self.rotate(Move("B"))
                self.rotate(Move("D"))
                self.rotate(Move("B", 3))
                self.rotate(Move("D", 3))
                self.rotate(Move("B"))
                self.rotate(Move("D"))
                self.rotate(Move("B", 3))

            elif self.pieces[1][1][0].orient == 2:
                self.rotate(Move("B"))
                self.rotate(Move("D", 3))
                self.rotate(Move("B", 3))
                self.rotate(Move("D"))
                self.rotate(Move("B"))
                self.rotate(Move("D", 3))
                self.rotate(Move("B", 3))

            if self.pieces[1][1][1].orient == 1:
                self.rotate(Move("R"))
                self.rotate(Move("D"))
                self.rotate(Move("R", 3))
                self.rotate(Move("D", 3))
                self.rotate(Move("R"))
                self.rotate(Move("D"))
                self.rotate(Move("R", 3))

            elif self.pieces[1][1][1].orient == 2:
                self.rotate(Move("R"))
                self.rotate(Move("D", 3))
                self.rotate(Move("R", 3))
                self.rotate(Move("D"))
                self.rotate(Move("R"))
                self.rotate(Move("D", 3))
                self.rotate(Move("R", 3))

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

            def rotate_edges():
                self.rotate(Move("R", 3))
                self.rotate(Move("D"))
                self.rotate(Move("L"))
                self.rotate(Move("D", 3))
                self.rotate(Move("R"))
                self.rotate(Move("D"))
                self.rotate(Move("L", 3))
                self.rotate(Move("D", 3))

            for z, z_row in enumerate(self.pieces):
                for y, y_row in enumerate(z_row):
                    for x, piece in enumerate(y_row):
                        if piece.col1 == self.yellow and piece.col2 == self.blue and piece.col3 == self.red:
                            if z == 1:
                                rotate_edges()
                                if x == 1:
                                    rotate_edges()

            if not ((piece := self.pieces[1][0][0]).col1 == self.yellow and piece.col2 == self.green and piece.col3 == self.orange):
                # back bottom left and back bottom right need to be swapped
                self.rotate(Move("L", 3))
                self.rotate(Move("D"))
                self.rotate(Move("R"))
                self.rotate(Move("D", 3))
                self.rotate(Move("L"))
                self.rotate(Move("D"))
                self.rotate(Move("R", 3))

                self.rotate(Move("D", 3))

                self.rotate(Move("L", 3))
                self.rotate(Move("D"))
                self.rotate(Move("R"))
                self.rotate(Move("D", 3))
                self.rotate(Move("L"))
                self.rotate(Move("D"))
                self.rotate(Move("R", 3))
