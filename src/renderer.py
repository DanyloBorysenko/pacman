from typing import List, Tuple
from src.state import GameState
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
            surface: pygame.Surface,
            cell_size: int) -> None:
        self.surface = surface
        self.cell_size = cell_size

    def draw(self, state: GameState) -> None:
        self._draw_maze(state.maze)
        self._draw_packman(state.pacman.row, state.pacman.col)

    def _draw_maze(self, maze: List[List[int]]) -> None:
        for row, line in enumerate(maze):
            for col, cell in enumerate(line):
                self._draw_cell(row, col, cell)

    def _draw_packman(self, row: int, col: int) -> None:
        center_x, center_y = self._cell_center(row, col)
        pygame.draw.circle(
            self.surface, PACK_MAN_COLOR,
            (center_x, center_y), self.cell_size // 3)

    def _draw_cell(self, row: int, col: int, cell: int) -> None:
        x, y = self._cell_top_left(row, col)
        if cell == 15:
            pygame.draw.rect(
                self.surface, MAZE_COLOR,
                (x, y, self.cell_size, self.cell_size))
            return

        if cell & NORTH:
            pygame.draw.line(
                self.surface, MAZE_COLOR,
                (x, y), (x + self.cell_size, y), WALL_WIDTH)
        if cell & EAST:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x + self.cell_size, y),
                (x + self.cell_size, y + self.cell_size), WALL_WIDTH)
        if cell & SOUTH:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y + self.cell_size),
                (x + self.cell_size, y + self.cell_size), WALL_WIDTH)
        if cell & WEST:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y),
                (x, y + self.cell_size), WALL_WIDTH)

    def _cell_top_left(self, row: int, col: int) -> Tuple[int, int]:
        return (col * self.cell_size, row * self.cell_size)

    def _cell_center(self, row: int, col: int) -> Tuple[int, int]:
        return (
            col * self.cell_size + self.cell_size // 2,
            row * self.cell_size + self.cell_size // 2
        )
