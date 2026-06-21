from typing import List, Tuple
from src.state import GameState, Direction
from src.constants import CELL_SIZE
import pygame

MAZE_COLOR = "turquoise"
PACK_MAN_COLOR = "yellow"
WALL_WIDTH = 5
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


class Renderer:
    def __init__(
            self,
            surface: pygame.Surface) -> None:
        self.surface = surface

    def draw(self, state: GameState) -> None:
        self.state = state
        self._draw_maze(state.maze)
        self._draw_packman(state.pacman.x, state.pacman.y)

    def _draw_maze(self, maze: List[List[int]]) -> None:
        for row, line in enumerate(maze):
            for col, cell in enumerate(line):
                self._draw_cell(row, col, cell)

    def _draw_packman(self, x: float, y: float) -> None:
        center_x = int(x)
        center_y = int(y)
        radius = CELL_SIZE // 3
        pygame.draw.circle(
            self.surface, PACK_MAN_COLOR,
            (center_x, center_y), radius)
        direction = (self.state.pacman.direction
                     if self.state.pacman.direction else Direction.RIGHT)
        dx, dy = direction.value
        if dx != 0:
            eye_x = center_x + (dx * (radius // 3))
            eye_y = center_y - (radius // 3)
        else:
            eye_x = center_x + (radius // 3)
            eye_y = center_y + (dy * (radius // 3))
        pygame.draw.circle(
            self.surface, "black", (eye_x, eye_y), radius // 5)

    def _draw_cell(self, row: int, col: int, cell: int) -> None:
        x, y = self._cell_top_left(row, col)
        if cell == 15:
            pygame.draw.rect(
                self.surface, MAZE_COLOR,
                (x, y, CELL_SIZE, CELL_SIZE))
            return

        if cell & NORTH:
            pygame.draw.line(
                self.surface, MAZE_COLOR,
                (x, y), (x + CELL_SIZE, y), WALL_WIDTH)
        if cell & EAST:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x + CELL_SIZE, y),
                (x + CELL_SIZE, y + CELL_SIZE), WALL_WIDTH)
        if cell & SOUTH:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y + CELL_SIZE),
                (x + CELL_SIZE, y + CELL_SIZE), WALL_WIDTH)
        if cell & WEST:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y),
                (x, y + CELL_SIZE), WALL_WIDTH)

    def _cell_top_left(self, row: int, col: int) -> Tuple[int, int]:
        return (col * CELL_SIZE, row * CELL_SIZE)

    def _cell_center(self, row: int, col: int) -> Tuple[int, int]:
        return (
            col * CELL_SIZE + CELL_SIZE // 2,
            row * CELL_SIZE + CELL_SIZE // 2
        )
