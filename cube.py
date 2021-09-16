from math3d import Mesh, Triangle, Vector3
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
        orange = "#ff2b00"
        blue = "#0000ff"
        green = "#00ff00"
        self.pieces = [
            [
                [
                    Corner(pos + Vector3(piece_width, piece_width, -piece_width), white, red, blue, piece_width)
                ],
                [
                ],
                [
                ]
            ],
            [
                [
                ],
                [
                ],
                [
                ]
            ],
            [
                [
                ],
                [
                ],
                [
                ]
            ],
        ]
