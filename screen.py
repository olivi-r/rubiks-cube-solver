from math3d import Camera, Triangle, Vector3
from cube import RubiksCube
import pygame

dimensions = [800, 450]
white = (255, 255, 255)


if __name__ == "__main__":
    pygame.display.set_caption("Rubik's Cube Solver")
    display = pygame.display.set_mode(dimensions)

    cam = Camera(Vector3(0, 0, -30), Vector3(0, 0, 0), 0.1)

    cube = RubiksCube(Vector3(0, 0, 0), 4)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # handle close button event
                running = False

        display.fill(white)

        for z in cube.pieces:
            for y in z:
                for piece in y:
                    for triangle in piece.triangles:
                        # convert world space triangle to camera space
                        new_triangle = Triangle(
                            cam.world_to_camera(triangle.p1),
                            cam.world_to_camera(triangle.p2),
                            cam.world_to_camera(triangle.p3),
                            triangle.col
                        )

                        if (triangle.p1 - cam.pos).dot(new_triangle.normal) > 0:
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
