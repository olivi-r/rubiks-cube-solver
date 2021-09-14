import pygame

dimensions = [800, 450]
white = (255, 255, 255)


if __name__ == "__main__":
    pygame.display.set_caption("Rubik's Cube Solver")
    display = pygame.display.set_mode(dimensions)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # handle close button event
                running = False

        display.fill(white)
        pygame.display.update()

    pygame.quit()
