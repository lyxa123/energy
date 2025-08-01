import pygame
import sys

print("Starting smoke test...")
try:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Smoke Test - Close window or press ESC to quit")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((0, 0, 255))  # Blue color
        pygame.display.flip()

    print("Smoke test finished successfully.")
except Exception as e:
    print(f"Smoke test failed: {e}")
finally:
    pygame.quit()
    sys.exit()
