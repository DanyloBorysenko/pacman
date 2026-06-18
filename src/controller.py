from src.renderer import Renderer
from typing import List
import pygame

CELL_SIZE = 50
# Controller now takes maze but we must change it on smt like
# class GameState:
#     maze: List[List[int]]


class Controller:
    def __init__(self, maze: List[List[int]]):
        pygame.init()
        self.width = CELL_SIZE * len(maze[0])
        self.height = CELL_SIZE * len(maze)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.Clock()
        self.maze = maze
        self.renderer = Renderer(self.screen, self.maze, CELL_SIZE)

    def run(self) -> None:
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.screen.fill("black")
            self.renderer.draw_maze()
            pygame.display.update()
        pygame.quit()
