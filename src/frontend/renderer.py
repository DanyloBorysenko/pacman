from typing import List, Tuple, Dict
from src.state import GameState, Direction, GameStats
from src.constants import CELL_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
from .scenes.models import MenuItem
from dataclasses import asdict
import pygame
import math

MAZE_COLOR = "turquoise"
PACK_MAN_COLOR = "yellow"
BACKGROUND_COLOR = "black"
ACCENT = "yellow"
INSTRUCTION_COLOR = "white"
MENU_FONT_SIZE = 50
INSTRUCTION_FONT_SIZE = 20
MENU_PADDING = 200
PADDING = 20
WALL_WIDTH = 5
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

# ── Layout constants (all relative to surface size) ──────────────────────────
_TITLE_Y_FRAC = 0.04   # title top edge as fraction of height
_BODY_TOP_FRAC = 0.14   # where columns start
_COL_LEFT_FRAC = 0.04   # left column x
_COL_RIGHT_FRAC = 0.52   # right column x
_LINE_H_FRAC = 0.038  # vertical step between lines
_FOOTER_BOT_FRAC = 0.97   # footer bottom edge


class Renderer:
    def __init__(
            self,
            surface: pygame.Surface) -> None:
        self.surface = surface
        self.menu_font = pygame.font.Font(size=MENU_FONT_SIZE)
        self.title_font = pygame.font.Font(None, 50)
        self.instruction_font = pygame.font.SysFont("DejaVu Sans", 24)
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
            surf = self.menu_font.render(item.value, True, PACK_MAN_COLOR)
            rect = surf.get_frect()
            rect.center = item_rect.center
            self.surface.blit(surf, rect)

    def draw_instructions(self) -> None:
        line_h = int(WINDOW_HEIGHT * _LINE_H_FRAC)
        left_x = int(WINDOW_WIDTH * _COL_LEFT_FRAC)
        right_x = int(WINDOW_WIDTH * _COL_RIGHT_FRAC)
        body_top = int(WINDOW_HEIGHT * _BODY_TOP_FRAC)

        # ── Helpers ──
        def blit_text(text: str, x: int, y: int,
                      color: str = "white",
                      font: pygame.font.Font | None = None) -> None:
            surf = (font or self.instruction_font).render(text, True, color)
            self.surface.blit(surf, (x, y))

        def draw_column(
                entries: list[tuple[str, str]], x: int, start_y: int) -> None:
            """
            entries: list of (text, color) pairs.
            An empty string inserts a blank line.
            """
            y = start_y
            for text, color in entries:
                if text:
                    blit_text(text, x, y, color)
                y += line_h

        blank = ("", INSTRUCTION_COLOR)      # empty-line sentinel

        left_column: list[tuple[str, str]] = [
            ("Controls",                    ACCENT),
            ("\u2191 / W    Move Up",        INSTRUCTION_COLOR),
            ("\u2193 / S    Move Down",      INSTRUCTION_COLOR),
            ("\u2190 / A    Move Left",      INSTRUCTION_COLOR),
            ("\u2192 / D    Move Right",     INSTRUCTION_COLOR),
            ("Space      Pause",             INSTRUCTION_COLOR),
            ("C           Cheat Mode",       INSTRUCTION_COLOR),
            blank,
            ("Pacgums",                      ACCENT),
            ("\u2022 Pacgum          +10 pts", INSTRUCTION_COLOR),
            ("\u2022 Super Pacgum    +50 pts", INSTRUCTION_COLOR),
            ("\u2022 Frightens ghosts",        INSTRUCTION_COLOR),
            ("  for [T] seconds",              INSTRUCTION_COLOR),
            blank,
            ("Winning",                      ACCENT),
            ("\u2022 Complete [N] levels",   INSTRUCTION_COLOR),
            ("\u2022 Eat every pacgum",      INSTRUCTION_COLOR),
        ]

        right_column: list[tuple[str, str]] = [
            ("Gameplay",                            ACCENT),
            ("\u2022 Start with 3 lives",            INSTRUCTION_COLOR),
            ("\u2022 Move only through corridors",   INSTRUCTION_COLOR),
            ("\u2022 Walls block movement",          INSTRUCTION_COLOR),
            ("\u2022 Touching a ghost loses a life", INSTRUCTION_COLOR),
            ("\u2022 Respawn in maze center",        INSTRUCTION_COLOR),
            ("\u2022 Game Over at 0 lives",          INSTRUCTION_COLOR),
            ("\u2022 Finish level by eating",        INSTRUCTION_COLOR),
            ("  every pacgum",                       INSTRUCTION_COLOR),
            blank,
            ("Ghosts",                               ACCENT),
            ("\u2022 Chase Pac-Man",                 INSTRUCTION_COLOR),
            ("\u2022 Run away when edible",          INSTRUCTION_COLOR),
            ("\u2022 Eat ghost: +200 pts",           INSTRUCTION_COLOR),
            ("\u2022 Respawn after [R] sec",         INSTRUCTION_COLOR),
            blank,
            ("Cheat Mode",                           ACCENT),
            ("\u2022 Invincibility",                 INSTRUCTION_COLOR),
            ("\u2022 Freeze Ghosts",                 INSTRUCTION_COLOR),
            ("\u2022 Level Skip",                    INSTRUCTION_COLOR),
            ("\u2022 Extra Lives",                   INSTRUCTION_COLOR),
            ("\u2022 Speed Boost",                   INSTRUCTION_COLOR),
        ]

        # ── Title ──
        title_surf = self.title_font.render(
            "PAC-MAN INSTRUCTIONS", True, ACCENT)
        title_rect = title_surf.get_frect()
        title_rect.centerx = WINDOW_WIDTH // 2
        title_rect.top = int(WINDOW_HEIGHT * _TITLE_Y_FRAC)
        self.surface.blit(title_surf, title_rect)

        # Separator line under title
        sep_y = int(title_rect.bottom + line_h * 0.4)
        pygame.draw.line(
            self.surface, ACCENT, (left_x, sep_y),
            (WINDOW_WIDTH - left_x, sep_y), 1)

        # ── Columns ──
        draw_column(left_column,  left_x,  body_top)
        draw_column(right_column, right_x, body_top)

        # ── Footer ──
        footer_surf = self.instruction_font.render(
            "ESC  -  Back to Menu", True, ACCENT)
        footer_rect = footer_surf.get_frect()
        footer_rect.left = left_x
        footer_rect.bottom = int(WINDOW_HEIGHT * _FOOTER_BOT_FRAC)
        self.surface.blit(footer_surf, footer_rect)

    def draw(self, state: GameState) -> None:
        self.state = state
        maze_width = CELL_SIZE * len(state.maze[0])
        maze_height = CELL_SIZE * len(state.maze)
        self.offset_x = (WINDOW_WIDTH - maze_width) // 2
        self.offset_y = (WINDOW_HEIGHT - maze_height) // 2
        self._draw_maze()
        self._draw_game_stats()
        self._draw_pacman()
        self._draw_gosts()

    def _draw_game_stats(self) -> None:
        stats = self.state.live_status

        center_y = WINDOW_HEIGHT // 2
        spacing = 40

        items = [
            f"Score:  {stats.current_score}",
            f"Level:  {stats.current_level}",
            f"Lives:  {stats.lives_remain}",
            f"Cheat mode:  {'On' if stats.cheat_mode else 'Off'}",
        ]
        start_y = center_y - ((len(items) - 1) * spacing) // 2

        for i, text in enumerate(items):
            surf = self.menu_font.render(text, True, PACK_MAN_COLOR)
            rect = surf.get_frect()
            rect.left = PADDING
            rect.centery = start_y + i * spacing
            self.surface.blit(surf, rect)

        if stats.time_left is not None:
            surf = self.menu_font.render(
                f"Time: {stats.time_left}",
                True,
                PACK_MAN_COLOR,
            )
            rect = surf.get_frect()
            rect.left = PADDING
            rect.bottom = WINDOW_HEIGHT - PADDING
            self.surface.blit(surf, rect)

    def _draw_maze(self) -> None:
        for row, line in enumerate(self.state.maze):
            for col, cell in enumerate(line):
                self._draw_cell(row, col, cell)

    def _draw_gosts(self) -> None:
        for ghost in self.state.ghosts:
            center_x = int(
                ghost.x * CELL_SIZE + self.offset_x + self.cell_offset)
            center_y = int(
                ghost.y * CELL_SIZE + self.offset_y + self.cell_offset)
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
