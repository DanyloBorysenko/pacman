from typing import List
import pygame

MAZE_COLOR = "white"
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

    def draw_maze(self, maze: List[List[int]]) -> None:
        for row, line in enumerate(maze):
            for col, cell in enumerate(line):
                self._draw_cell(row, col, cell)

    def _draw_cell(self, row: int, col: int, cell: int) -> None:
        x = col * self.cell_size
        y = row * self.cell_size
        if cell & NORTH:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y), (x + self.cell_size, y), 5)
        if cell & EAST:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x + self.cell_size, y), (x + self.cell_size, y + self.cell_size), 5)
        if cell & SOUTH:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y + self.cell_size), (x + self.cell_size, y + self.cell_size), 5)
        if cell & WEST:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y), (x, y + self.cell_size), 5)