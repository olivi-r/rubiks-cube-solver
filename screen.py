from math3d import Camera, Matrix3x3, Polygon, Triangle, Vector2, Vector3, rot_x, rot_y, rot_z
from cube import Center, Corner, Edge, RubiksCube
import os; os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import sys
import pygame
import tkinter
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showwarning


def bubble_sort(to_sort: list) -> None:
    # sort list in-place w/ bubble sort algorithm
    swapped = True
    while swapped:
        swapped = False
        for i, val in enumerate(to_sort):
            try:
                if val[0] > to_sort[i + 1][0]:
                    to_sort[i], to_sort[i + 1] = to_sort[i + 1], to_sort[i]
                    swapped = True

            except IndexError:
                break


def sign(p1: list, p2: list, p3: list) -> float:
    # https://stackoverflow.com/a/2049593
    return (p1.i - p3.i) * (p2.j - p3.j) - (p2.i - p3.i) * (p1.j - p3.j)


def drag_face(cube: RubiksCube, cam: Camera, mouse_delta: Vector2, vectors: dict) -> None:
    new_vecs = {}
    if cube.layers == 3:
        rot = global_rotation3x3

    elif cube.layers == 2:
        rot = global_rotation2x2

    for move, vec in vectors.items():
        new_vec = cam.world_to_camera(rot * vec)
        new_vec = Vector2(new_vec.i, -new_vec.j)
        new_vec.normalize()
        new_vecs[move] = new_vec.dot(mouse_delta)

    for k, v in new_vecs.items():
        if max(new_vecs.values()) == v:
            # rotate by most similar direction
            cube.evaluate(k)
            return


dimensions = [800, 450]

wireframe = False

if __name__ == "__main__":
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 12)
    move_font = pygame.font.SysFont("Arial", 24)
    move_font_active = pygame.font.SysFont("Arial", 32)
    pygame.display.set_caption("Rubik's Cube Solver")

    # allow program to find icon files in bundled executable mode
    logo_dir = sys._MEIPASS if hasattr(sys, "_MEIPASS") else ""

    # create window for tkinter's save dialog to use and hide it
    headless_container = tkinter.Tk()
    headless_container.withdraw()
    headless_container.iconbitmap(os.path.join(logo_dir, "logo.ico"))
    headless_container.update()

    display = pygame.display.set_mode(dimensions, pygame.RESIZABLE)

    icon_image = pygame.image.load(os.path.join(logo_dir, "logo.png"))
    pygame.display.set_icon(icon_image)

    cam = Camera(Vector3(0, 0, -30), Vector3(0, 0, 0), 0.1)

    cube3x3 = RubiksCube(12, 3, 125)
    cube2x2 = RubiksCube(12, 2, 125)
    cube = cube3x3

    global_rotation3x3 = Matrix3x3([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    global_rotation2x2 = Matrix3x3([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    dragging = False
    dragging_piece = False
    piece_selected = False
    selected_piece = None

    solve_btn_selected = False
    scramble_btn_selected = False

    back_arrow_selected = False
    forward_arrow_selected = False

    fps_counter = pygame.time.Clock()

    btn_not_selected = (255, 255, 255)
    btn_selected = (200, 200, 200)

    swap_selected = False

    save_selected = False
    load_selected = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # handle close button event
                running = False

            if event.type == pygame.VIDEORESIZE:
                # adjust content when window resized

                # clamp minimun size
                size = [
                    max(event.size[0], 685),
                    max(event.size[1], 343)
                ]
                dimensions = size
                display = pygame.display.set_mode(dimensions, pygame.RESIZABLE)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not dragging:
                        if swap_selected:
                            if cube.layers == 2:
                                cube = cube3x3

                            elif cube.layers == 3:
                                cube = cube2x2

                        if solve_btn_selected:
                            cube.solve()

                        elif scramble_btn_selected:
                            cube.scramble()

                        # going through the cube's past moves
                        elif back_arrow_selected:
                            if cube.history_index > 0:
                                move = cube.history[cube.history_index].opposite
                                cube.rotate(move, True, False)
                                cube.history_index -= 1

                        elif forward_arrow_selected:
                            if cube.history_index < len(cube.history) - 1:
                                cube.history_index += 1
                                move = cube.history[cube.history_index]
                                cube.rotate(move, True, False)

                        elif save_selected:
                            state = cube3x3.save_state(global_rotation3x3)
                            state += "\n"
                            state += cube2x2.save_state(global_rotation2x2)

                            name = asksaveasfilename(initialfile="rubiks cube.save", defaultextension=".save", filetypes=[
                                ("Save File", "*.save"), ("All files", "*.*")
                            ])
                            if name != "":
                                with open(name, "w+") as fp:
                                    fp.write(state)

                        elif load_selected:
                            name = askopenfilename(filetypes=[
                                ("Save File", "*.save"), ("All files", "*.*")
                            ])
                            if os.path.exists(name):
                                with open(name, "r") as fp:
                                    # try:
                                    state3x3, state2x2 = fp.read().split("\n")
                                    cube3x3, global_rotation3x3 = cube.load_state(state3x3)
                                    cube2x2, global_rotation2x2 = cube.load_state(state2x2)
                                    if cube.layers == 3:
                                        cube = cube3x3

                                    elif cube.layers == 2:
                                        cube = cube2x2

                                    # except:
                                    #     showwarning(
                                    #         "Rubik's Cube Solver",
                                    #         "Invalid Save File"
                                    #     )

                        elif pygame.mouse.get_pos()[1] > 40:
                            # dragging the cube's rotation
                            if piece_selected:
                                dragging_piece = True

                            else:
                                dragging = True

                            pygame.mouse.get_rel()

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                dragging_piece = False

            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    # convert mouse motion into global rotations for cube
                    mouse_delta = pygame.mouse.get_rel()
                    delta = rot_x(0.4 * mouse_delta[1]) * rot_y(0.4 * mouse_delta[0])
                    if cube.layers == 3:
                        global_rotation3x3 = delta * global_rotation3x3

                    elif cube.layers == 2:
                        global_rotation2x2 = delta * global_rotation2x2

                elif dragging_piece:
                    if cube.moving or cube.moving_threads:
                        selected_piece = None
                        dragging_piece = False
                        continue

                    mouse_delta = Vector2(*pygame.mouse.get_rel())
                    if mouse_delta.magnitude < 10:
                        # need sufficient movment to move pieces, makes it harder to rotate wrong direction
                        continue

                    pieces = [piece for z in cube.tmp_pieces for y in z for piece in y]
                    try:
                        x = pieces.index(selected_piece[0])

                    except ValueError:
                        selected_piece = None
                        dragging_piece = False
                        continue

                    z = x // cube.layers ** 2
                    y = x // cube.layers % cube.layers
                    x %= cube.layers

                    if isinstance(selected_piece[0], Corner):
                        # top, front and right of original meshes, not position
                        orient_map = {
                            "top": {
                                0: 0,
                                1: 2,
                                2: 1
                            },
                            "front": {
                                0: 1,
                                1: 0,
                                2: 2
                            },
                            "right": {
                                0: 2,
                                1: 1,
                                2: 0
                            }
                        }

                        # top left front corner
                        if x == 0 and y == cube.layers - 1 and z == 0:
                            if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                # top side
                                vecs = {
                                    "L": Vector3(0, 0, -1),
                                    "L'": Vector3(0, 0, 1),
                                    "F": Vector3(1, 0, 0),
                                    "F'": Vector3(-1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                # front side
                                vecs = {
                                    "U": Vector3(0, 0, 1),
                                    "U'": Vector3(0, 0, -1),
                                    "F": Vector3(0, 1, 0),
                                    "F'": Vector3(0, -1, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["right"][selected_piece[0].orient] == selected_piece[1]:
                                # right side
                                vecs = {
                                    "U": Vector3(-1, 0, 0),
                                    "U'": Vector3(1, 0, 0),
                                    "L": Vector3(0, -1, 0),
                                    "L'": Vector3(0, 1, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                        # top right front corner
                        if x == cube.layers - 1 and y == cube.layers - 1 and z == 0:
                            if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                # top side
                                vecs = {
                                    "R": Vector3(0, 0, 1),
                                    "R'": Vector3(0, 0, -1),
                                    "F": Vector3(1, 0, 0),
                                    "F'": Vector3(-1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                # front side
                                vecs = {
                                    "U": Vector3(-1, 0, 0),
                                    "U'": Vector3(1, 0, 0),
                                    "R": Vector3(0, 1, 0),
                                    "R'": Vector3(0, -1, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["right"][selected_piece[0].orient] == selected_piece[1]:
                                # right side
                                vecs = {
                                    "U": Vector3(0, 0, -1),
                                    "U'": Vector3(0, 0, 1),
                                    "F": Vector3(0, -1, 0),
                                    "F'": Vector3(0, 1, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                        # top left back corner
                        if x == 0 and y == cube.layers - 1 and z == cube.layers - 1:
                            if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                # top side
                                vecs = {
                                    "L": Vector3(0, 0, -1),
                                    "L'": Vector3(0, 0, 1),
                                    "B": Vector3(-1, 0, 0),
                                    "B'": Vector3(1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                # front side
                                vecs = {
                                    "U": Vector3(1, 0, 0),
                                    "U'": Vector3(-1, 0, 0),
                                    "L": Vector3(0, 1, 0),
                                    "L'": Vector3(0, -1, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["right"][selected_piece[0].orient] == selected_piece[1]:
                                # right side
                                vecs = {
                                    "U": Vector3(0, 0, 1),
                                    "U'": Vector3(0, 0, -1),
                                    "B": Vector3(0, -1, 0),
                                    "B'": Vector3(0, 1, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                        # top right back corner
                        if x == cube.layers - 1 and y == cube.layers - 1 and z == cube.layers - 1:
                            if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                # top side
                                vecs = {
                                    "R": Vector3(0, 0, 1),
                                    "R'": Vector3(0, 0, -1),
                                    "B": Vector3(-1, 0, 0),
                                    "B'": Vector3(1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                # front side
                                vecs = {
                                    "U": Vector3(0, 0, -1),
                                    "U'": Vector3(0, 0, 1),
                                    "B": Vector3(0, 1, 0),
                                    "B'": Vector3(0, -1, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["right"][selected_piece[0].orient] == selected_piece[1]:
                                # right side
                                vecs = {
                                    "U": Vector3(1, 0, 0),
                                    "U'": Vector3(-1, 0, 0),
                                    "R": Vector3(0, -1, 0),
                                    "R'": Vector3(0, 1, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                        # bottom left front corner
                        if x == 0 and y == 0 and z == 0:
                            if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                # top side
                                vecs = {
                                    "L": Vector3(0, 0, 1),
                                    "L'": Vector3(0, 0, -1),
                                    "F": Vector3(-1, 0, 0),
                                    "F'": Vector3(1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                # front side
                                vecs = {
                                    "L": Vector3(0, -1, 0),
                                    "L'": Vector3(0, 1, 0),
                                    "D": Vector3(1, 0, 0),
                                    "D'": Vector3(-1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["right"][selected_piece[0].orient] == selected_piece[1]:
                                # right side
                                vecs = {
                                    "F": Vector3(0, 1, 0),
                                    "F'": Vector3(0, -1, 0),
                                    "D": Vector3(0, 0, -1),
                                    "D'": Vector3(0, 0, 1)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                        # bottom right front corner
                        if x == cube.layers - 1 and y == 0 and z == 0:
                            if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                # top side
                                vecs = {
                                    "R": Vector3(0, 0, -1),
                                    "R'": Vector3(0, 0, 1),
                                    "F": Vector3(-1, 0, 0),
                                    "F'": Vector3(1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                # front side
                                vecs = {
                                    "F": Vector3(0, -1, 0),
                                    "F'": Vector3(0, 1, 0),
                                    "D": Vector3(0, 0, 1),
                                    "D'": Vector3(0, 0, -1)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["right"][selected_piece[0].orient] == selected_piece[1]:
                                # right side
                                vecs = {
                                    "R": Vector3(0, 1, 0),
                                    "R'": Vector3(0, -1, 0),
                                    "D": Vector3(1, 0, 0),
                                    "D'": Vector3(-1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                        # bottom left back corner
                        if x == 0 and y == 0 and z == cube.layers - 1:
                            if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                # top side
                                vecs = {
                                    "L": Vector3(0, 0, 1),
                                    "L'": Vector3(0, 0, -1),
                                    "B": Vector3(1, 0, 0),
                                    "B'": Vector3(-1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                # front side
                                vecs = {
                                    "B": Vector3(0, -1, 0),
                                    "B'": Vector3(0, 1, 0),
                                    "D": Vector3(0, 0, -1),
                                    "D'": Vector3(0, 0, 1)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["right"][selected_piece[0].orient] == selected_piece[1]:
                                # right side
                                vecs = {
                                    "L": Vector3(0, 1, 0),
                                    "L'": Vector3(0, -1, 0),
                                    "D": Vector3(-1, 0, 0),
                                    "D'": Vector3(1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                        # bottom right back corner
                        if x == cube.layers - 1 and y == 0 and z == cube.layers - 1:
                            if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                # top side
                                vecs = {
                                    "R": Vector3(0, 0, -1),
                                    "R'": Vector3(0, 0, 1),
                                    "B": Vector3(1, 0, 0),
                                    "B'": Vector3(-1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                # front side
                                vecs = {
                                    "R": Vector3(0, -1, 0),
                                    "R'": Vector3(0, 1, 0),
                                    "D": Vector3(-1, 0, 0),
                                    "D'": Vector3(1, 0, 0)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                            elif orient_map["right"][selected_piece[0].orient] == selected_piece[1]:
                                # right side
                                vecs = {
                                    "B": Vector3(0, 1, 0),
                                    "B'": Vector3(0, -1, 0),
                                    "D": Vector3(0, 0, 1),
                                    "D'": Vector3(0, 0, -1)
                                }

                                drag_face(cube, cam, mouse_delta, vecs)

                    elif isinstance(selected_piece[0], Center):
                        if x == 0:
                            # left centers
                            vecs = {
                                f"D'.{y}": Vector3(0, 0, 1),
                                f"D.{y}": Vector3(0, 0, -1),
                                f"F.{z}": Vector3(0, 1, 0),
                                f"F'.{z}": Vector3(0, -1, 0)
                            }

                            drag_face(cube, cam, mouse_delta, vecs)

                        elif x == cube.layers - 1:
                            # right centers
                            vecs = {
                                f"D.{y}": Vector3(0, 0, 1),
                                f"D'.{y}": Vector3(0, 0, -1),
                                f"F'.{z}": Vector3(0, 1, 0),
                                f"F.{z}": Vector3(0, -1, 0)
                            }

                            drag_face(cube, cam, mouse_delta, vecs)

                        elif y == 0:
                            # bottom centers
                            vecs = {
                                f"L.{x}": Vector3(0, 0, 1),
                                f"L'.{x}": Vector3(0, 0, -1),
                                f"F'.{z}": Vector3(1, 0, 0),
                                f"F.{z}": Vector3(-1, 0, 0)
                            }

                            drag_face(cube, cam, mouse_delta, vecs)

                        elif y == cube.layers - 1:
                            # top centers
                            vecs = {
                                f"L'.{x}": Vector3(0, 0, 1),
                                f"L.{x}": Vector3(0, 0, -1),
                                f"F.{z}": Vector3(1, 0, 0),
                                f"F'.{z}": Vector3(-1, 0, 0)
                            }

                            drag_face(cube, cam, mouse_delta, vecs)

                        elif z == 0:
                            # front centers
                            vecs = {
                                f"L'.{x}": Vector3(0, 1, 0),
                                f"L.{x}": Vector3(0, -1, 0),
                                f"D.{y}": Vector3(1, 0, 0),
                                f"D'.{y}": Vector3(-1, 0, 0)
                            }

                            drag_face(cube, cam, mouse_delta, vecs)

                        elif z == cube.layers - 1:
                            # back centers
                            vecs = {
                                f"L.{x}": Vector3(0, 1, 0),
                                f"L'.{x}": Vector3(0, -1, 0),
                                f"D'.{y}": Vector3(1, 0, 0),
                                f"D.{y}": Vector3(-1, 0, 0)
                            }

                            drag_face(cube, cam, mouse_delta, vecs)

                    elif isinstance(selected_piece[0], Edge):
                        orient_map = {
                            "top": {
                                0: 0,
                                1: 1,
                                2: 0,
                                3: 1
                            },
                            "front": {
                                0: 1,
                                1: 0,
                                2: 1,
                                3: 0
                            }
                        }
                        if x == 0:
                            # left side
                            if y == 0:
                                # bottom left
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "L": Vector3(0, 0, 1),
                                        "L'": Vector3(0, 0, -1),
                                        f"F.{z}": Vector3(-1, 0, 0),
                                        f"F'.{z}": Vector3(1, 0, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "D": Vector3(0, 0, -1),
                                        "D'": Vector3(0, 0, 1),
                                        f"F.{z}": Vector3(0, 1, 0),
                                        f"F'.{z}": Vector3(0, -1, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                            elif y == cube.layers - 1:
                                # top left
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "L": Vector3(0, 0, -1),
                                        "L'": Vector3(0, 0, 1),
                                        f"F.{z}": Vector3(1, 0, 0),
                                        f"F'.{z}": Vector3(-1, 0, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "U": Vector3(0, 0, 1),
                                        "U'": Vector3(0, 0, -1),
                                        f"F.{z}": Vector3(0, 1, 0),
                                        f"F'.{z}": Vector3(0, -1, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                            elif z == 0:
                                # front left
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "F": Vector3(0, 1, 0),
                                        "F'": Vector3(0, -1, 0),
                                        f"D.{y}": Vector3(0, 0, -1),
                                        f"D'.{y}": Vector3(0, 0, 1)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "L": Vector3(0, -1, 0),
                                        "L'": Vector3(0, 1, 0),
                                        f"D.{y}": Vector3(1, 0, 0),
                                        f"D'.{y}": Vector3(-1, 0, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                            elif z == cube.layers - 1:
                                # back left
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "B": Vector3(0, -1, 0),
                                        "B'": Vector3(0, 1, 0),
                                        f"D.{y}": Vector3(0, 0, -1),
                                        f"D'.{y}": Vector3(0, 0, 1)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "L": Vector3(0, 1, 0),
                                        "L'": Vector3(0, -1, 0),
                                        f"D.{y}": Vector3(-1, 0, 0),
                                        f"D'.{y}": Vector3(1, 0, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                        elif x == cube.layers - 1:
                            # right side
                            if y == 0:
                                # bottom right
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "R": Vector3(0, 0, -1),
                                        "R'": Vector3(0, 0, 1),
                                        f"F.{z}": Vector3(-1, 0, 0),
                                        f"F'.{z}": Vector3(1, 0, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "D": Vector3(0, 0, 1),
                                        "D'": Vector3(0, 0, -1),
                                        f"F.{z}": Vector3(0, -1, 0),
                                        f"F'.{z}": Vector3(0, 1, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                            elif y == cube.layers - 1:
                                # top right
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "R": Vector3(0, 0, 1),
                                        "R'": Vector3(0, 0, -1),
                                        f"F.{z}": Vector3(1, 0, 0),
                                        f"F'.{z}": Vector3(-1, 0, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "U": Vector3(0, 0, -1),
                                        "U'": Vector3(0, 0, 1),
                                        f"F.{z}": Vector3(0, -1, 0),
                                        f"F'.{z}": Vector3(0, 1, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                            elif z == 0:
                                # front right
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "F": Vector3(0, -1, 0),
                                        "F'": Vector3(0, 1, 0),
                                        f"D.{y}": Vector3(0, 0, 1),
                                        f"D'.{y}": Vector3(0, 0, -1)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "R": Vector3(0, 1, 0),
                                        "R'": Vector3(0, -1, 0),
                                        f"D.{y}": Vector3(1, 0, 0),
                                        f"D'.{y}": Vector3(-1, 0, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                            elif z == cube.layers - 1:
                                # back right
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "B": Vector3(0, 1, 0),
                                        "B'": Vector3(0, -1, 0),
                                        f"D.{y}": Vector3(0, 0, 1),
                                        f"D'.{y}": Vector3(0, 0, -1)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "R": Vector3(0, -1, 0),
                                        "R'": Vector3(0, 1, 0),
                                        f"D.{y}": Vector3(-1, 0, 0),
                                        f"D'.{y}": Vector3(1, 0, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                        elif y == 0:
                            # bottom side
                            if z == 0:
                                # bottom front
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "F": Vector3(-1, 0, 0),
                                        "F'": Vector3(1, 0, 0),
                                        f"L.{x}": Vector3(0, 0, 1),
                                        f"L'.{x}": Vector3(0, 0, -1)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "D": Vector3(1, 0, 0),
                                        "D'": Vector3(-1, 0, 0),
                                        f"L.{x}": Vector3(0, -1, 0),
                                        f"L'.{x}": Vector3(0, 1, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                            elif z == cube.layers - 1:
                                # bottom back
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "B": Vector3(1, 0, 0),
                                        "B'": Vector3(-1, 0, 0),
                                        f"L.{x}": Vector3(0, 0, 1),
                                        f"L'.{x}": Vector3(0, 0, -1)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "D": Vector3(-1, 0, 0),
                                        "D'": Vector3(1, 0, 0),
                                        f"L.{x}": Vector3(0, 1, 0),
                                        f"L'.{x}": Vector3(0, -1, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                        elif y == cube.layers - 1:
                            # top side
                            if z == 0:
                                # top front
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "F": Vector3(1, 0, 0),
                                        "F'": Vector3(-1, 0, 0),
                                        f"L.{x}": Vector3(0, 0, -1),
                                        f"L'.{x}": Vector3(0, 0, 1)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "U": Vector3(-1, 0, 0),
                                        "U'": Vector3(1, 0, 0),
                                        f"L.{x}": Vector3(0, -1, 0),
                                        f"L'.{x}": Vector3(0, 1, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                            elif z == cube.layers - 1:
                                # top back
                                if orient_map["top"][selected_piece[0].orient] == selected_piece[1]:
                                    # top side
                                    vecs = {
                                        "B": Vector3(-1, 0, 0),
                                        "B'": Vector3(1, 0, 0),
                                        f"L.{x}": Vector3(0, 0, -1),
                                        f"L'.{x}": Vector3(0, 0, 1)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

                                elif orient_map["front"][selected_piece[0].orient] == selected_piece[1]:
                                    # front side
                                    vecs = {
                                        "U": Vector3(1, 0, 0),
                                        "U'": Vector3(-1, 0, 0),
                                        f"L.{x}": Vector3(0, 1, 0),
                                        f"L'.{x}": Vector3(0, -1, 0)
                                    }

                                    drag_face(cube, cam, mouse_delta, vecs)

        display.fill((255, 255, 255))

        # line to separate history and cube view
        pygame.draw.line(display, (0, 0, 0), (0, 40), (dimensions[0], 40))

        to_draw = []
        for z in cube.tmp_pieces:
            for y in z:
                for piece in y:
                    if piece is None:
                        continue

                    tmp_piece = piece.copy()
                    if cube.layers == 3:
                        tmp_piece.rotate(global_rotation3x3)

                    elif cube.layers == 2:
                        tmp_piece.rotate(global_rotation2x2)

                    for face, poly in enumerate(tmp_piece.polys):
                        backface = False
                        if (poly.triangles[0].p1 - cam.pos).dot(poly.normal) > 0:
                            # remove backfaces when cube isn't moving to maximise frame rate
                            # backfaces are otherwise coloured in black
                            if cube.moving or wireframe:
                                backface = True

                            else:
                                continue

                        new_poly = Polygon()
                        depths = []
                        for triangle in poly.triangles:
                            # convert world space triangle to camera space
                            new_triangle = Triangle(
                                cam.world_to_camera(triangle.p1),
                                cam.world_to_camera(triangle.p2),
                                cam.world_to_camera(triangle.p3),
                                triangle.col if not backface else "#000000"
                            )
                            new_poly.triangles.append(new_triangle)

                            # get the average distance of the camera space triangle from the camera
                            avg_depth = new_triangle.p1.magnitude
                            avg_depth += new_triangle.p2.magnitude
                            avg_depth += new_triangle.p3.magnitude
                            avg_depth /= 3
                            depths.append(avg_depth)

                        overall_avg_depth = sum(depths) / len(depths)
                        to_draw.append([overall_avg_depth, new_poly, piece, face])

        if not dragging_piece or cube.moving:
            piece_selected = False
            selected_piece = None
            dragging_piece = False

        bubble_sort(to_draw)
        for poly in reversed(to_draw):
            # project 3D camera space points to 2D plane

            cached_points = {}

            selected = False
            if not dragging:
                for tri in poly[1].triangles:
                    # https://stackoverflow.com/a/2049593
                    # construct a ray to detect intersections with polygons from mouse position
                    if selected:
                        continue

                    # project 3D camera space points to 2D plane
                    points = (
                        cam.project2d(tri.p1, *dimensions),
                        cam.project2d(tri.p2, *dimensions),
                        cam.project2d(tri.p3, *dimensions)
                    )

                    cached_points[tri] = points

                    # calculate if mouse intersecting triangle
                    coords = Vector2(*pygame.mouse.get_pos())
                    deltas = [
                        sign(coords, points[0], points[1]),
                        sign(coords, points[1], points[2]),
                        sign(coords, points[2], points[0])
                    ]
                    neg = any(map(lambda x: x < 0, deltas))
                    pos = any(map(lambda x: x > 0, deltas))
                    if not selected:
                        if dragging_piece:
                            if poly[2] == selected_piece[0] and poly[3] == selected_piece[1]:
                                selected = True

                        else:
                            selected = not (neg and pos)

                    if not piece_selected and selected:
                        piece_selected = True
                        selected_piece = poly[2:]

            for tri in poly[1].triangles:
                try:
                    points = cached_points[tri]

                except KeyError:
                    # project 3D camera space points to 2D plane
                    points = (
                        cam.project2d(tri.p1, *dimensions),
                        cam.project2d(tri.p2, *dimensions),
                        cam.project2d(tri.p3, *dimensions)
                    )

                # draw shapes
                points = [[vec.i, vec.j] for vec in points]
                if not selected:
                    pygame.draw.polygon(display, tri.col, points, width=10 if wireframe else 0)

                else:
                    pygame.draw.polygon(display, cube.dimmed[tri.col], points, width=10 if wireframe else 0)

                pygame.draw.lines(display, "#000000", wireframe, points, width=5)

        # display fps in top left
        fps_counter.tick()
        fps = fps_counter.get_fps()
        fps_text = font.render(f"FPS: {int(fps)}", True, (0, 0, 0))
        display.blit(fps_text, (5, 5))

        # display move history and controls
        if cube.history[cube.history_index] is not None:
            move_text = move_font_active.render(repr(cube.history[cube.history_index]), True, (0, 0, 0))
            display.blit(move_text, (dimensions[0] / 2, 0))

        if cube.history_index > 1:
            move_text_l1 = move_font.render(repr(cube.history[cube.history_index - 1]), True, (127, 127, 127))
            display.blit(move_text_l1, (5 * dimensions[0] / 12, 5))

            if cube.history_index > 2:
                move_text_l2 = move_font.render(repr(cube.history[cube.history_index - 2]), True, (190, 190, 190))
                display.blit(move_text_l2, (4 * dimensions[0] / 12, 7))

        if cube.history_index < len(cube.history) - 1:
            move_text_r1 = move_font.render(repr(cube.history[cube.history_index + 1]), True, (127, 127, 127))
            display.blit(move_text_r1, (7 * dimensions[0] / 12, 5))
            if cube.history_index < len(cube.history) - 2:
                move_text_r2 = move_font.render(repr(cube.history[cube.history_index + 2]), True, (190, 190, 190))
                display.blit(move_text_r2, (8 * dimensions[0] / 12, 7))

        back_arrow_points = [
            Vector2(3 * dimensions[0] / 12 - 10, 20),
            Vector2(3 * dimensions[0] / 12 + 10, 10),
            Vector2(3 * dimensions[0] / 12 + 10, 30)
        ]
        deltas = [
            sign(coords, back_arrow_points[0], back_arrow_points[1]),
            sign(coords, back_arrow_points[1], back_arrow_points[2]),
            sign(coords, back_arrow_points[2], back_arrow_points[0])
        ]
        neg = any(map(lambda x: x < 0, deltas))
        pos = any(map(lambda x: x > 0, deltas))
        if not (neg and pos):
            back_arrow_selected = True

        else:
            back_arrow_selected = False

        pygame.draw.polygon(
            display,
            (100, 100, 100) if back_arrow_selected else (190, 190, 190),
            list(map(lambda x: [x.i, x.j], back_arrow_points))
        )

        forward_arrow_points = [
            Vector2(9 * dimensions[0] / 12 + 10, 20),
            Vector2(9 * dimensions[0] / 12 - 10, 10),
            Vector2(9 * dimensions[0] / 12 - 10, 30)
        ]
        deltas = [
            sign(coords, forward_arrow_points[0], forward_arrow_points[1]),
            sign(coords, forward_arrow_points[1], forward_arrow_points[2]),
            sign(coords, forward_arrow_points[2], forward_arrow_points[0])
        ]
        neg = any(map(lambda x: x < 0, deltas))
        pos = any(map(lambda x: x > 0, deltas))
        if not (neg and pos):
            forward_arrow_selected = True

        else:
            forward_arrow_selected = False

        pygame.draw.polygon(
            display,
            (100, 100, 100) if forward_arrow_selected else (190, 190, 190),
            list(map(lambda x: [x.i, x.j], forward_arrow_points))
        )

        # scramble button
        scramble_btn = pygame.rect.Rect(dimensions[0] / 12 - 2, 7, 88, 25)

        pygame.draw.rect(
            display,
            btn_selected if scramble_btn_selected else btn_not_selected,
            scramble_btn
        )

        scramble_btn_text = move_font.render("Scramble", True, (0, 0, 0))
        display.blit(scramble_btn_text, (dimensions[0] / 12, 5))

        # solve button
        solve_btn = pygame.rect.Rect(10 * dimensions[0] / 12 - 2, 7, 53, 25)

        pygame.draw.rect(
            display,
            btn_selected if solve_btn_selected else btn_not_selected,
            solve_btn
        )

        solve_btn_text = move_font.render("Solve", True, (0, 0, 0))
        display.blit(solve_btn_text, (10 * dimensions[0] / 12, 5))

        # detect hovering over buttons
        scramble_btn_selected = scramble_btn.collidepoint(coords.i, coords.j)
        solve_btn_selected = solve_btn.collidepoint(coords.i, coords.j)


        # save button
        save_offset = [dimensions[0] / 30, 19 * dimensions[1] / 20]

        save_btn = pygame.rect.Rect(
            save_offset[0] - 5, save_offset[1] - 18, 28, 33
        )

        save_selected = save_btn.collidepoint(coords.i, coords.j)

        pygame.draw.rect(
            display, (200, 200, 200) if save_selected else (255, 255, 255),
            save_btn
        )

        colour = (0, 0, 0) if save_selected else (127, 127, 127)

        pygame.draw.line(
            display, colour, save_offset,
            [save_offset[0], save_offset[1] + 7], width=2
        )
        pygame.draw.line(
            display, colour, [save_offset[0] + 16, save_offset[1]],
            [save_offset[0] + 16, save_offset[1] + 7], width=2
        )
        pygame.draw.line(
            display, colour, [save_offset[0], save_offset[1] + 8],
            [save_offset[0] + 17, save_offset[1] + 8], width=2
        )
        pygame.draw.line(
            display, colour, [save_offset[0] + 8, save_offset[1] - 13],
            [save_offset[0] + 8, save_offset[1] + 3], width=2
        )
        pygame.draw.line(
            display, colour, [save_offset[0] + 8, save_offset[1] + 3],
            [save_offset[0], save_offset[1] - 5], width = 2
        )
        pygame.draw.line(
            display, colour, [save_offset[0] + 8, save_offset[1] + 3],
            [save_offset[0] + 16, save_offset[1] - 5], width = 2
        )

        # load button
        load_offset = [2.5 * dimensions[0] / 30, 19 * dimensions[1] / 20]

        load_btn = pygame.rect.Rect(
            load_offset[0] - 5, load_offset[1] - 18, 28, 33
        )

        load_selected = load_btn.collidepoint(coords.i, coords.j)

        pygame.draw.rect(
            display, (200, 200, 200) if load_selected else (255, 255, 255),
            load_btn
        )

        colour = (0, 0, 0) if load_selected else (127, 127, 127)

        pygame.draw.line(
            display, colour, load_offset,
            [load_offset[0], load_offset[1] + 7], width=2
        )
        pygame.draw.line(
            display, colour, [load_offset[0] + 16, load_offset[1]],
            [load_offset[0] + 16, load_offset[1] + 7], width=2
        )
        pygame.draw.line(
            display, colour, [load_offset[0], load_offset[1] + 8],
            [load_offset[0] + 17, load_offset[1] + 8], width=2
        )
        pygame.draw.line(
            display, colour, [load_offset[0] + 8, load_offset[1] - 13],
            [load_offset[0] + 8, load_offset[1] + 3], width=2
        )
        pygame.draw.line(
            display, colour, [load_offset[0] + 8, load_offset[1] - 13],
            [load_offset[0], load_offset[1] - 5], width = 2
        )
        pygame.draw.line(
            display, colour, [load_offset[0] + 8, load_offset[1] - 13],
            [load_offset[0] + 16, load_offset[1] - 5], width = 2
        )


        swap_offset = [19 * dimensions[0] / 20, 18 * dimensions[1] / 20]
        swap_bbox = pygame.rect.Rect(
            swap_offset[0] - 5, swap_offset[1] - 5,
            32 if cube.layers == 3 else 44, 32 if cube.layers == 3 else 44
        )
        two_x_two_symbol = [
            pygame.rect.Rect(*swap_offset, 10, 10),
            pygame.rect.Rect(swap_offset[0], swap_offset[1] + 12, 10, 10),
            pygame.rect.Rect(swap_offset[0] + 12, swap_offset[1], 10, 10),
            pygame.rect.Rect(swap_offset[0] + 12, swap_offset[1] + 12, 10, 10)
        ]

        three_x_three_symbol = [
            pygame.rect.Rect(*swap_offset, 10, 10),
            pygame.rect.Rect(swap_offset[0], swap_offset[1] + 12, 10, 10),
            pygame.rect.Rect(swap_offset[0], swap_offset[1] + 24, 10, 10),
            pygame.rect.Rect(swap_offset[0] + 12, swap_offset[1], 10, 10),
            pygame.rect.Rect(swap_offset[0] + 12, swap_offset[1] + 12, 10, 10),
            pygame.rect.Rect(swap_offset[0] + 12, swap_offset[1] + 24, 10, 10),
            pygame.rect.Rect(swap_offset[0] + 24, swap_offset[1], 10, 10),
            pygame.rect.Rect(swap_offset[0] + 24, swap_offset[1] + 12, 10, 10),
            pygame.rect.Rect(swap_offset[0] + 24, swap_offset[1] + 24, 10, 10)
        ]

        swap_selected = swap_bbox.collidepoint(coords.i, coords.j)

        pygame.draw.rect(
            display,
            (200, 200, 200) if swap_selected else (255, 255, 255),
            swap_bbox
        )

        if cube.layers == 2:
            for rect in three_x_three_symbol:
                pygame.draw.rect(
                    display,
                    (127, 127, 127) if swap_selected else (200, 200, 200),
                    rect
                )

        else:
            for rect in two_x_two_symbol:
                pygame.draw.rect(
                    display,
                    (127, 127, 127) if swap_selected else (200, 200, 200),
                    rect
                )

        pygame.display.update()

    pygame.quit()
    cube.running = False
