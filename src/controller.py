from src.renderer import Renderer
from src.state import GameState, Direction
from src.logic import GameLogic
from src.constants import CELL_SIZE
from typing import List
import pygame


class Controller:
    def __init__(self, state: GameState, logic: GameLogic):
        pygame.init()
        self.logic = logic
        self.state = state
        self.width = CELL_SIZE * len(self.state.maze[0])
        self.height = CELL_SIZE * len(self.state.maze)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.Clock()
        self.renderer = Renderer(self.screen)

    def run(self) -> None:
        self.running = True
        while self.running:
            dt = self.clock.tick(60) / 1000
            self._process_events()
            self.logic.update(self.state, dt)
            self.screen.fill("black")
            self.renderer.draw(self.state)
            pygame.display.update()
        pygame.quit()

    def _process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.logic.update_direction(self.state, Direction.UP)
                if event.key == pygame.K_DOWN:
                    self.logic.update_direction(self.state, Direction.DOWN)
                if event.key == pygame.K_LEFT:
                    self.logic.update_direction(self.state, Direction.LEFT)
                if event.key == pygame.K_RIGHT:
                    self.logic.update_direction(self.state, Direction.RIGHT)
                if event.key == pygame.K_SPACE:
                    self.logic.apply_pause(self.state)
