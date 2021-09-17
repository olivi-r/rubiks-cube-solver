from math3d import Mesh, Triangle, Vector3, rot_x, rot_y, rot_z
import re

hex_col = re.compile(r"#[\dA-Za-z]{6}")


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


class RubiksCube:
    def __init__(self, pos: Vector3, piece_width: float):
        white = "#ffffff"
        yellow = "#ffff00"
        red = "#ff0000"
        orange = "#ff6f00"
        blue = "#0000ff"
        green = "#00ff00"
        self.pieces = [
            [
                [
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), yellow, red, green, piece_width),
                    Edge(pos + Vector3(0, piece_width, -piece_width), yellow, red, piece_width),
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), blue, red, yellow, piece_width)
                ],
                [
                    Edge(pos + Vector3(0, piece_width, -piece_width), green, red, piece_width),
                    Center(pos + Vector3(0, piece_width, 0), red, piece_width),
                    Edge(pos + Vector3(0, piece_width, -piece_width), blue, red, piece_width)
                ],
                [
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), white, green, red, piece_width),
                    Edge(pos + Vector3(0, piece_width, -piece_width), white, red, piece_width),
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), white, red, blue, piece_width)
                ]
            ],
            [
                [
                    Edge(pos + Vector3(0, piece_width, -piece_width), yellow, green, piece_width),
                    Center(pos + Vector3(0, piece_width, 0), yellow, piece_width),
                    Edge(pos + Vector3(0, piece_width, -piece_width), yellow, blue, piece_width)
                ],
                [
                    Center(pos + Vector3(0, piece_width, 0), green, piece_width),
                    None,
                    Center(pos + Vector3(0, piece_width, 0), blue, piece_width)
                ],
                [
                    Edge(pos + Vector3(0, piece_width, -piece_width), white, green, piece_width),
                    Center(pos + Vector3(0, piece_width, 0), white, piece_width),
                    Edge(pos + Vector3(0, piece_width, -piece_width), white, blue, piece_width)
                ]
            ],
            [
                [
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), green, orange, yellow, piece_width),
                    Edge(pos + Vector3(0, piece_width, -piece_width), yellow, orange, piece_width),
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), yellow, orange, blue, piece_width)
                ],
                [
                    Edge(pos + Vector3(0, piece_width, -piece_width), green, orange, piece_width),
                    Center(pos + Vector3(0, piece_width, 0), orange, piece_width),
                    Edge(pos + Vector3(0, piece_width, -piece_width), blue, orange, piece_width)
                ],
                [
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), white, orange, green, piece_width),
                    Edge(pos + Vector3(0, piece_width, -piece_width), white, orange, piece_width),
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), white, blue, orange, piece_width)
                ]
            ],
        ]

        # rotate pieces into place
        # front
        self.pieces[0][0][0].rotate(rot_z(180))
        self.pieces[0][0][1].rotate(rot_z(180))
        self.pieces[0][0][2].rotate(rot_z(90))
        self.pieces[0][1][0].rotate(rot_z(-90))
        self.pieces[0][1][1].rotate(rot_x(90))
        self.pieces[0][1][2].rotate(rot_z(90))
        self.pieces[0][2][0].rotate(rot_y(-90))

        # middle
        self.pieces[1][0][0].rotate(rot_y(-90))
        self.pieces[1][0][0].rotate(rot_x(180))
        self.pieces[1][0][1].rotate(rot_z(180))
        self.pieces[1][0][2].rotate(rot_y(90))
        self.pieces[1][0][2].rotate(rot_x(180))
        self.pieces[1][1][0].rotate(rot_z(-90))
        self.pieces[1][1][2].rotate(rot_z(90))
        self.pieces[1][2][0].rotate(rot_y(-90))
        self.pieces[1][2][2].rotate(rot_y(90))

        # back
        self.pieces[2][0][0].rotate(rot_y(180))
        self.pieces[2][0][0].rotate(rot_z(-90))
        self.pieces[2][0][1].rotate(rot_y(180))
        self.pieces[2][0][1].rotate(rot_z(180))
        self.pieces[2][0][2].rotate(rot_y(180))
        self.pieces[2][0][2].rotate(rot_z(180))
        self.pieces[2][1][0].rotate(rot_y(180))
        self.pieces[2][1][0].rotate(rot_z(-90))
        self.pieces[2][1][1].rotate(rot_x(-90))
        self.pieces[2][1][2].rotate(rot_y(180))
        self.pieces[2][1][2].rotate(rot_z(90))
        self.pieces[2][2][0].rotate(rot_y(180))
        self.pieces[2][2][1].rotate(rot_y(180))
        self.pieces[2][2][2].rotate(rot_y(90))
