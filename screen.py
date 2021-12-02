from math3d import Camera, Matrix3x3, Polygon, Triangle, Vector2, Vector3, rot_x, rot_y, rot_z
from cube import RubiksCube
import os; os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import tkinter
from tkinter.filedialog import askopenfilename, asksaveasfilename


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
    for move, vec in vecs.items():
        new_vec = cam.world_to_camera(global_rotation * vec)
        new_vec = Vector2(new_vec.i, -new_vec.j)
        new_vec.normalize()
        new_vecs[move] = new_vec.dot(mouse_delta)

    for k, v in new_vecs.items():
        if max(new_vecs.values()) == v:
            cube.evaluate(k)
            return


dimensions = [800, 450]

display_mode = False
wireframe = False

if __name__ == "__main__":
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 12)
    pygame.display.set_caption("Rubik's Cube Solver")

    # create window for tkinter's save dialog to use and hide it
    headless_container = tkinter.Tk()
    headless_container.withdraw()
    headless_container.update()

    display = pygame.display.set_mode(dimensions, pygame.RESIZABLE)

    cam = Camera(Vector3(0, 0, -30), Vector3(0, 0, 0), 0.1)

    cube = RubiksCube(12, 3, 250, display_mode)

    display_angle = rot_z(45) * rot_x(45)
    global_rotation = Matrix3x3([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    if display_mode:
        global_rotation = display_angle * global_rotation

    dragging = False
    dragging_piece = False
    piece_selected = False
    selected_piece = None

    fps_counter = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # handle close button event
                running = False

            if event.type == pygame.VIDEORESIZE:
                # adjust content when window resized
                dimensions = event.size

            if not display_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        name = asksaveasfilename(initialfile="rubiks cube.save", defaultextension=".save", filetypes=[
                            ("All files", "*.*"), ("Save state", "*.save")
                        ])
                        if name != "":
                            with open(name, "w+") as fp:
                                fp.write(cube.save_state(global_rotation))

                    if event.key == pygame.K_a:
                        name = askopenfilename(defaultextension=".save", filetypes=[
                            ("All files", "*.*"), ("Save state", "*.save")
                        ])
                        if os.path.exists(name):
                            with open(name, "r") as fp:
                                cube, global_rotation = cube.load_state(fp.read())

                    if event.key == pygame.K_0:
                        cube.scramble()

                    if event.key == pygame.K_1:
                        cube.solve()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not dragging:
                            if piece_selected:
                                dragging_piece = True

                            else:
                                dragging = True

                            pygame.mouse.get_rel()

                if event.type == pygame.MOUSEMOTION:
                    if dragging:
                        # convert mouse motion into global rotations for cube
                        mouse_delta = pygame.mouse.get_rel()
                        global_rotation = rot_x(0.25 * mouse_delta[1]) * global_rotation
                        global_rotation = rot_y(0.25 * mouse_delta[0]) * global_rotation

                    elif dragging_piece:
                        if not (cube.moving or cube.moving_threads):
                            mouse_delta = Vector2(*pygame.mouse.get_rel())
                            if mouse_delta.magnitude < 10:
                                # need sufficient movment to move pieces
                                continue

                            pieces = [piece for z in cube.tmp_pieces for y in z for piece in y]
                            x = pieces.index(selected_piece[0])
                            z = x // cube.layers ** 2
                            y = x // cube.layers % cube.layers
                            x %= cube.layers

                            orient_map = {
                                "top": {
                                    0: 0,
                                    1: 2,
                                    2: 1
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

                if event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                    dragging_piece = False

        display.fill((255, 255, 255))

        to_draw = []
        for z in cube.tmp_pieces:
            for y in z:
                for piece in y:
                    if piece is None:
                        continue

                    tmp_piece = piece.copy()
                    tmp_piece.rotate(global_rotation)
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
                if not selected or display_mode:
                    pygame.draw.polygon(display, tri.col, points, width=10 if wireframe else 0)

                else:
                    pygame.draw.polygon(display, cube.dimmed[tri.col], points, width=10 if wireframe else 0)

                pygame.draw.lines(display, "#000000", wireframe, points, width=5)

        # display fps in top left
        fps_counter.tick()
        fps = fps_counter.get_fps()
        fps_text = font.render(f"FPS: {int(fps)}", False, (0, 0, 0))
        display.blit(fps_text, (5, 5))
        pygame.display.update()

        if display_mode and fps != 0:
            # frame independently rotate the cube slowly around y-axis
            global_rotation = rot_y(10 / fps) * global_rotation

    pygame.quit()
    cube.running = False
