from math3d import Camera, Matrix3x3, Triangle, Vector3, rot_x, rot_y
from cube import RubiksCube
import pygame

dimensions = [800, 450]
white = (255, 255, 255)


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

        display.fill(white)

        for z in cube.pieces:
            for y in z:
                for piece in y:
                    if piece is None:
                        continue

                    tmp_piece = piece.copy()
                    tmp_piece.rotate(global_rotation)
                    for triangle in tmp_piece.triangles:
                        # convert world space triangle to camera space
                        new_triangle = Triangle(
                            cam.world_to_camera(triangle.p1),
                            cam.world_to_camera(triangle.p2),
                            cam.world_to_camera(triangle.p3),
                            triangle.col
                        )

                        if (triangle.p1 - cam.pos).dot(triangle.normal) > 0:
                            # remove faces pointing away from camera
                            continue

                        # project 3D camera space points to 2D plane
                        points = (
                            cam.project2d(new_triangle.p1, *dimensions),
                            cam.project2d(new_triangle.p2, *dimensions),
                            cam.project2d(new_triangle.p3, *dimensions)
                        )

                        # draw shapes
                        pygame.draw.polygon(display, new_triangle.col, points)
                        pygame.draw.lines(display, "#000000", False, points)

        pygame.display.update()

    pygame.quit()
