from math3d import Camera, Matrix3x3, Polygon, Triangle, Vector3, rot_x, rot_y
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
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


dimensions = [800, 450]


if __name__ == "__main__":
    pygame.display.set_caption("Rubik's Cube Solver")

    # create window for tkinter's save dialog to use and hide it
    headless_container = tkinter.Tk()
    headless_container.withdraw()
    headless_container.update()

    display = pygame.display.set_mode(dimensions, pygame.RESIZABLE)

    cam = Camera(Vector3(0, 0, -30), Vector3(0, 0, 0), 0.1)

    cube = RubiksCube(12, 3, 100)

    global_rotation = Matrix3x3([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    dragging = False
    piece_selected = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # handle close button event
                running = False

            if event.type == pygame.VIDEORESIZE:
                # adjust content when window resized
                dimensions = event.size

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
                    if not dragging and not piece_selected:
                        dragging = True
                        pygame.mouse.get_rel()

            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_delta = pygame.mouse.get_rel()
                    global_rotation = rot_x(0.25 * mouse_delta[1]) * global_rotation
                    global_rotation = rot_y(0.25 * mouse_delta[0]) * global_rotation

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False

        display.fill((255, 255, 255))

        to_draw = []
        for z in cube.tmp_pieces:
            for y in z:
                for piece in y:
                    if piece is None:
                        continue

                    tmp_piece = piece.copy()
                    tmp_piece.rotate(global_rotation)
                    for poly in tmp_piece.polys:
                        backface = False
                        if (poly.triangles[0].p1 - cam.pos).dot(poly.normal) > 0:
                            # faces pointing away from camera
                            backface = True

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
                        to_draw.append([overall_avg_depth, new_poly])

        piece_selected = False
        bubble_sort(to_draw)
        for poly in reversed(to_draw):
            # project 3D camera space points to 2D plane

            selected = False
            if not dragging:
                for tri in poly[1].triangles:
                    # https://stackoverflow.com/a/2049593
                    # construct a ray to detect intersections with polygons from mouse position
                    if selected:
                        continue

                    points = (
                        cam.project2d(tri.p1, *dimensions),
                        cam.project2d(tri.p2, *dimensions),
                        cam.project2d(tri.p3, *dimensions)
                    )

                    coords = pygame.mouse.get_pos()
                    deltas = [
                        sign(coords, points[0], points[1]),
                        sign(coords, points[1], points[2]),
                        sign(coords, points[2], points[0])
                    ]
                    neg = any(map(lambda x: x < 0, deltas))
                    pos = any(map(lambda x: x > 0, deltas))
                    if not selected:
                        selected = not (neg and pos)

                    if not piece_selected and selected:
                        piece_selected = True

            for tri in poly[1].triangles:
                # project 3D camera space points to 2D plane
                points = (
                    cam.project2d(tri.p1, *dimensions),
                    cam.project2d(tri.p2, *dimensions),
                    cam.project2d(tri.p3, *dimensions)
                )
                # draw shapes
                if not selected:
                    pygame.draw.polygon(display, tri.col, points)

                else:
                    pygame.draw.polygon(display, cube.dimmed[tri.col], points)

                pygame.draw.lines(display, "#000000", False, points, width=5)

        pygame.display.update()

    pygame.quit()
    cube.running = False
