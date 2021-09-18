from math3d import Camera, Matrix3x3, Triangle, Vector3, rot_x, rot_y
from cube import RubiksCube
import pygame


def bubble_sort(to_sort: list) -> None:
    # sort list in-place w/ bubble sort algorithm
    swapped = True
    while swapped:
        swapped = False
        for i, val in enumerate(to_sort):
            try:
                if val[0] > to_sort[i + 1][0]:
                    to_sort[i], to_sort[i + 1] = to_sort[i + 1], to_sort[i]
                    # to_sort[i : i + 1] = reversed(to_sort[i + 1 : i - 1])
                    swapped = True

            except IndexError:
                break


dimensions = [800, 450]


if __name__ == "__main__":
    pygame.display.set_caption("Rubik's Cube Solver")
    display = pygame.display.set_mode(dimensions)

    cam = Camera(Vector3(0, 0, -30), Vector3(0, 0, 0), 0.1)

    cube = RubiksCube(Vector3(0, 0, 0), 4)

    global_rotation = Matrix3x3([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    dragging = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # handle close button event
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    cube.rotate_back()

                if event.key == pygame.K_f:
                    cube.rotate_front()

                if event.key == pygame.K_r:
                    cube.rotate_right()

                if event.key == pygame.K_l:
                    cube.rotate_left()

                if event.key == pygame.K_u:
                    cube.rotate_up()

                if event.key == pygame.K_d:
                    cube.rotate_down()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not dragging:
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
        for z in cube.pieces:
            for y in z:
                for piece in y:
                    if piece is None:
                        continue

                    tmp_piece = piece.copy()
                    tmp_piece.rotate(global_rotation)
                    for triangle in tmp_piece.triangles:
                        if (triangle.p1 - cam.pos).dot(triangle.normal) > 0:
                            # remove faces pointing away from camera
                            continue

                        # convert world space triangle to camera space
                        new_triangle = Triangle(
                            cam.world_to_camera(triangle.p1),
                            cam.world_to_camera(triangle.p2),
                            cam.world_to_camera(triangle.p3),
                            triangle.col
                        )

                        # get the average distance of the camera space triangle from the camera
                        avg_depth = new_triangle.p1.magnitude
                        avg_depth += new_triangle.p2.magnitude
                        avg_depth += new_triangle.p3.magnitude
                        avg_depth /= 3

                        to_draw.append([avg_depth, new_triangle])

        bubble_sort(to_draw)
        for tri in reversed(to_draw):
            # project 3D camera space points to 2D plane
            points = (
                cam.project2d(tri[1].p1, *dimensions),
                cam.project2d(tri[1].p2, *dimensions),
                cam.project2d(tri[1].p3, *dimensions)
            )

            # draw shapes
            pygame.draw.polygon(display, tri[1].col, points)
            pygame.draw.lines(display, "#000000", False, points)

        pygame.display.update()

    pygame.quit()
