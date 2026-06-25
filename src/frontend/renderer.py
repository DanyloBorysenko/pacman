from typing import List, Tuple
from src.state import GameState, Direction
from src.constants import CELL_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
from .scenes.models import MenuItem
import pygame
import math

MAZE_COLOR = "turquoise"
PACK_MAN_COLOR = "yellow"
BACKGROUND_COLOR = "black"
MENU_FONT_SIZE = 50
MENU_PADDING = 200
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
        self.menu_font = pygame.font.Font(size=MENU_FONT_SIZE)
        self.offset_x = 0
        self.offset_y = 0
        self.cell_offset = CELL_SIZE // 2

    def draw_main_menu(self, sel_item: int, items: List[MenuItem]) -> None:
        count = len(items)
        item_height = (WINDOW_HEIGHT - MENU_PADDING * 2) // count
        item_width = WINDOW_WIDTH // 5
        for ind, item in enumerate(items):
            item_surf = pygame.Surface((item_width, item_height))
            item_rect = item_surf.get_frect()
            item_rect.center = (
                WINDOW_WIDTH // 2,
                MENU_PADDING + (ind * item_height) + item_height // 2)
            if sel_item == ind:
                pygame.draw.rect(
                    self.surface, pygame.Color(50, 50, 50), item_rect)
            surf = self.menu_font.render(item.value, True, "yellow")
            rect = surf.get_frect()
            rect.center = item_rect.center
            self.surface.blit(surf, rect)

    def draw(self, state: GameState) -> None:
        self.state = state
        maze_width = CELL_SIZE * len(state.maze[0])
        maze_height = CELL_SIZE * len(state.maze)
        self.offset_x = (WINDOW_WIDTH - maze_width) // 2
        self.offset_y = (WINDOW_HEIGHT - maze_height) // 2
        self._draw_maze()
        self._draw_pacman()
        self._draw_gosts()

    def _draw_maze(self) -> None:
        for row, line in enumerate(self.state.maze):
            for col, cell in enumerate(line):
                self._draw_cell(row, col, cell)

    def _draw_gosts(self) -> None:
        for ghost in self.state.ghosts:
            center_x = int(ghost.x * CELL_SIZE + self.offset_x + self.cell_offset)
            center_y = int(ghost.y * CELL_SIZE + self.offset_y + self.cell_offset)
            radius = CELL_SIZE // 3
            pygame.draw.circle(
                self.surface, ghost.colour, (center_x, center_y), radius)
            eye_surf = pygame.Surface((radius // 2.5, radius // 2))
            left_eye_rect = eye_surf.get_frect()
            left_eye_rect.center = (center_x - radius // 2, center_y - radius // 3)
            pygame.draw.ellipse(self.surface, "white", left_eye_rect)
            right_eye_rect = eye_surf.get_frect()
            right_eye_rect.center = (center_x + radius // 2, center_y - radius // 3)
            pygame.draw.ellipse(self.surface, "white", right_eye_rect)

    def _draw_pacman(self) -> None:
        pacman = self.state.pacman
        center_x = int(pacman.x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(pacman.y * CELL_SIZE + self.offset_y + self.cell_offset)
        radius = CELL_SIZE // 3
        pygame.draw.circle(
            self.surface, PACK_MAN_COLOR,
            (center_x, center_y), radius)
        direction = (pacman.direction
                     if pacman.direction else Direction.RIGHT)
        dx, dy = direction.value
        if dx != 0:
            eye_x = center_x + (dx * (radius // 3))
            eye_y = center_y - (radius // 3)
        else:
            eye_x = center_x + (radius // 3)
            eye_y = center_y + (dy * (radius // 3))
        pygame.draw.circle(
            self.surface, BACKGROUND_COLOR, (eye_x, eye_y), radius // 5)
        chomp_factor = abs(math.sin(pacman.mouth_phase))

        # Perpendicular vectors for jaw spread
        perpendicular_x = -dy
        perpendicular_y = dx

        # Calculate the tip of the mouth extending outward
        mouth_tip_x = center_x + dx * (radius)
        mouth_tip_y = center_y + dy * (radius)

        # Apply the chomp_factor to the maximum jaw spread width
        max_jaw_spread = radius // 2
        current_jaw_spread = max_jaw_spread * chomp_factor

        # Calculate the two shifting corners of the mouth
        jaw1_x = mouth_tip_x + perpendicular_x * current_jaw_spread
        jaw1_y = mouth_tip_y + perpendicular_y * current_jaw_spread

        jaw2_x = mouth_tip_x - perpendicular_x * current_jaw_spread
        jaw2_y = mouth_tip_y - perpendicular_y * current_jaw_spread

        # 4. Draw the animating mouth polygon
        mouth_points = [
            (center_x, center_y),
            (int(jaw1_x), int(jaw1_y)),
            (int(jaw2_x), int(jaw2_y))
        ]
        pygame.draw.polygon(self.surface, BACKGROUND_COLOR, mouth_points)

    def _draw_cell(self, row: int, col: int, cell: int) -> None:
        x, y = self._cell_top_left(row, col)
        x = x + self.offset_x
        y = y + self.offset_y
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

        center_pos = (x + self.cell_offset, y + self.cell_offset)
        if cell & 32:
            pygame.draw.circle(self.surface, (255, 255, 0), center_pos, 8)
        elif cell & 16:
            pygame.draw.circle(self.surface, (255, 184, 151), center_pos, 3)

    def _cell_top_left(self, row: int, col: int) -> Tuple[int, int]:
        return (col * CELL_SIZE, row * CELL_SIZE)
