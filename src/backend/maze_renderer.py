import sys
import numpy as np
import pygame

# Bitmask Constants
NORTH = 1
SOUTH = 4
WEST = 8
EAST = 2

PACGUM = 16
SUPER_PACGUM = 32

FPS = 60

# Colors (RGB)
BG_COLOR = (0, 0, 0)
WALL_COLOR = (33, 33, 255)       # Classic Arcade Blue
GUM_COLOR = (255, 184, 151)      # Soft Peach/Yellow
SUPER_GUM_COLOR = (255, 255, 0)  # Bright Yellow

def generate_maze(raw_maze: np.ndarray, TILE_SIZE: int = 40) -> None:
    # Initialize Pygame explicitly
    pygame.init()
    screen = pygame.display.set_mode((raw_maze.shape[1] * TILE_SIZE, raw_maze.shape[0] * TILE_SIZE))
    pygame.display.set_caption("Pac-Man Architecture Test")
    clock = pygame.time.Clock()

    # Execution Flags
    running = True
    
    # THE CORE ARCADE LOOP
    while running:
        # Crucial Step 1: Pump OS window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Crucial Step 2: Clear layout canvas with pure black background
        screen.fill((0, 0, 0))

        # Crucial Step 3: Iterate and draw shapes based on bitwise matrices
        for y in range(raw_maze.shape[0]):
            for x in range(raw_maze.shape[1]):
                val = raw_maze[y, x]
                pixel_x = x * TILE_SIZE
                pixel_y = y * TILE_SIZE
                
                # Check walls mask
                if (val & 15) > 0:
                    if val & NORTH:
                        pygame.draw.line(screen, (33, 33, 255), (pixel_x, pixel_y), (pixel_x + TILE_SIZE, pixel_y), 3)
                    if val & SOUTH:
                        pygame.draw.line(screen, (33, 33, 255), (pixel_x, pixel_y + TILE_SIZE), (pixel_x + TILE_SIZE, pixel_y + TILE_SIZE), 3)
                    if val & WEST:
                        pygame.draw.line(screen, (33, 33, 255), (pixel_x, pixel_y), (pixel_x, pixel_y + TILE_SIZE), 3)
                    if val & EAST:
                        pygame.draw.line(screen, (33, 33, 255), (pixel_x + TILE_SIZE, pixel_y), (pixel_x + TILE_SIZE, pixel_y + TILE_SIZE), 3)

                center_pos = (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)
                if val & SUPER_PACGUM:
                    pygame.draw.circle(screen, (255, 255, 0), center_pos, 8)
                elif val & PACGUM:
                    pygame.draw.circle(screen, (255, 184, 151), center_pos, 3)

        # Crucial Step 4: Force display pipeline flip
        pygame.display.flip()
        
        # Maintain execution cadence at 60 Frames Per Second
        clock.tick(60)

    pygame.quit()


# =====================================================================
# Verification Execution
# =====================================================================
if __name__ == "__main__":
    # Your 10x10 test maze
    raw_maze = np.array([
        [11, 13,  1,  1,  1,  5,  5,  1,  1,  7],
        [ 8,  1,  2, 10, 12,  1,  3, 12,  0,  3],
        [10, 10, 10,  8,  1,  2, 12,  3, 12,  2],
        [10, 10, 12,  2, 10, 12,  5,  4,  1,  2],
        [10, 12,  1,  2, 12,  1,  3,  9,  2, 10],
        [ 8,  1,  6,  8,  1,  6, 10,  8,  2, 10],
        [10, 12,  1,  4,  0,  1,  2, 10, 12,  2],
        [ 8,  1,  4,  1,  4,  6, 10, 10,  9,  6],
        [ 8,  2,  9,  2,  9,  5,  6, 10,  8,  3],
        [12,  4,  4,  4,  4,  5,  5,  4,  4,  6]
    ])

    # Inject items using our bitwise offsets
    raw_maze[1, 8] |= PACGUM
    raw_maze[6, 4] |= SUPER_PACGUM

    # Increase TILE_SIZE to 40 or 50 if your screen has high resolution
    TILE_SIZE = 40
    generate_maze(TILE_SIZE=TILE_SIZE, raw_maze=raw_maze)
