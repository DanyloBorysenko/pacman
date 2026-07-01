from typing import List, Tuple
from src.state import GameState, Direction, Ghost
from src.constants import CELL_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
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
        self.center_x = WINDOW_WIDTH // 2
        self.center_y = WINDOW_HEIGHT // 2
        self.line_h = int(WINDOW_HEIGHT * _LINE_H_FRAC)
        self.left_x = int(WINDOW_WIDTH * _COL_LEFT_FRAC)

    def draw_menu(self, sel_item: int, items: List[str], title: str) -> None:
        title_rect = self._draw_title(title)
        available_height = WINDOW_HEIGHT - title_rect.bottom
        count = len(items)
        if count == 0:
            return
        spacing = 20

        item_width = WINDOW_WIDTH // 4
        item_height = (available_height - (spacing * (count + 1))) // count
        max_height = 60
        item_height = min(item_height, max_height)
        total_menu_height = (count * item_height) + ((count - 1) * spacing)
        start_y = (title_rect.bottom +
                   (available_height - total_menu_height) // 2)
        for ind, item in enumerate(items):
            item_surf = pygame.Surface((item_width, item_height))
            item_rect = item_surf.get_frect()
            center_y = start_y + (ind * (item_height + spacing)) + (
                item_height // 2)
            item_rect.center = (self.center_x, center_y)
            if sel_item == ind:
                pygame.draw.rect(
                    self.surface,
                    pygame.Color(50, 50, 50), item_rect, border_radius=6
                )
            surf = self.menu_font.render(item, True, PACK_MAN_COLOR)
            rect = surf.get_frect()
            rect.center = item_rect.center
            self.surface.blit(surf, rect)

    def draw_instructions(self) -> None:
        right_x = int(WINDOW_WIDTH * _COL_RIGHT_FRAC)
        body_top = int(WINDOW_HEIGHT * _BODY_TOP_FRAC)

        # ── Helpers ──
        def blit_text(text: str, x: int, y: int,
                      color: str = "white") -> None:
            surf = self.instruction_font.render(text, True, color)
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
                y += self.line_h

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

        self._draw_title("PAC-MAN INSTRUCTIONS")

        # ── Columns ──
        draw_column(left_column,  self.left_x,  body_top)
        draw_column(right_column, right_x, body_top)

        self._escape_footer()

    def draw_highscores(self, data: List[Tuple[str, str, str]]) -> None:
        title_rect = self._draw_title("Highscores")
        count = len(data)
        if count == 0:
            return

        available_height = WINDOW_HEIGHT - title_rect.bottom
        spacing = 15
        line_height = min(
            (available_height - (spacing * (count + 1))) // count, 50)
        total_score_height = (count * line_height) + ((count - 1) * spacing)
        start_y = title_rect.bottom + (
            (available_height - total_score_height) // 2)
        for ind, line in enumerate(data):
            player, level, score = line
            surf = self.instruction_font.render(
                f"{player}    {level}    {score}", True, "white"
            )
            rect = surf.get_frect()
            center_y = start_y + (
                ind * (line_height + spacing)) + (line_height // 2)
            rect.center = (self.center_x, center_y)
            self.surface.blit(surf, rect)

        self._escape_footer()

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

    def draw_victory(self, sel_item: int) -> None:
        self._escape_footer()
        surf = self.menu_font.render("VICTORY!!!", True, "green")
        rect = surf.get_frect()
        rect.center = (self.center_x, PADDING * 2)
        self.surface.blit(surf, rect)
        self._draw_question_menu(sel_item)

    def draw_defeat(self, sel_item: int) -> None:
        self._escape_footer()
        surf = self.menu_font.render("GAME OVER!!!", True, "red")
        rect = surf.get_frect()
        rect.center = (self.center_x, PADDING * 2)
        self.surface.blit(surf, rect)
        self._draw_question_menu(sel_item)

    def _draw_question_menu(self, sel_item: int) -> None:
        surf = self.title_font.render(
            "Would you like to save your result?", True, "white")
        rect = surf.get_frect()
        rect.center = (self.center_x, self.center_y - WINDOW_HEIGHT // 4)
        self.surface.blit(surf, rect)

        button_surf = pygame.Surface((WINDOW_WIDTH // 5, WINDOW_HEIGHT // 12))
        left_rect = button_surf.get_frect()
        left_rect.midright = (int(self.center_x - 30), self.center_y)
        right_rect = button_surf.get_frect()
        right_rect.midleft = (int(self.center_x + 30), self.center_y)
        if sel_item == 0:
            pygame.draw.rect(
                self.surface,
                pygame.Color(50, 50, 50), left_rect, border_radius=6
                )
        else:
            pygame.draw.rect(
                self.surface,
                pygame.Color(50, 50, 50), right_rect, border_radius=6
                )
        yes_surf = self.menu_font.render("YES", True, "white")
        yes_rect = yes_surf.get_frect()
        yes_rect.center = left_rect.center
        self.surface.blit(yes_surf, yes_rect)

        no_surf = self.menu_font.render("NO", True, "white")
        no_rect = no_surf.get_frect()
        no_rect.center = right_rect.center
        self.surface.blit(no_surf, no_rect)

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

    def _draw_ghost(self, ghost: Ghost) -> None:
        center_x = int(ghost.x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(ghost.y * CELL_SIZE + self.offset_y + self.cell_offset)

        radius = CELL_SIZE // 3

        # ----- head -----
        pygame.draw.circle(
            self.surface,
            ghost.colour,
            (center_x, center_y - radius // 3),
            radius,
        )

        # ----- body -----
        body = pygame.Rect(
            center_x - radius,
            center_y - radius // 3,
            radius * 2,
            radius + radius // 3,
        )
        pygame.draw.rect(self.surface, ghost.colour, body)

        # ----- bottom waves -----
        wave_r = radius // 3
        bottom = body.bottom

        for x in (
            center_x - radius + wave_r,
            center_x,
            center_x + radius - wave_r,
        ):
            pygame.draw.circle(
                self.surface,
                ghost.colour,
                (x, bottom),
                wave_r,
            )

        # ----- eyes -----
        eye_w = radius // 2
        eye_h = radius

        left_eye = pygame.Rect(0, 0, eye_w, eye_h)
        left_eye.center = (
            center_x - radius // 3,
            center_y - radius // 2,
        )

        right_eye = pygame.Rect(0, 0, eye_w, eye_h)
        right_eye.center = (
            center_x + radius // 3,
            center_y - radius // 2,
        )

        pygame.draw.ellipse(self.surface, "white", left_eye)
        pygame.draw.ellipse(self.surface, "white", right_eye)

        pupil = radius // 6

        dx, dy = ghost.assigned_direction.value

        offset = radius // 8

        pygame.draw.circle(
            self.surface,
            "blue",
            (
                left_eye.centerx + dx * offset,
                left_eye.centery + dy * offset,
            ),
            pupil,
        )

        pygame.draw.circle(
            self.surface,
            "blue",
            (
                right_eye.centerx + dx * offset,
                right_eye.centery + dy * offset,
            ),
            pupil,
        )

    def _draw_gosts(self) -> None:
        for ghost in self.state.ghosts:
            self._draw_ghost(ghost)

    def _draw_pacman(self) -> None:
        pacman = self.state.pacman

        center_x = int(pacman.x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(pacman.y * CELL_SIZE + self.offset_y + self.cell_offset)
        radius = CELL_SIZE // 3

        # Draw body
        pygame.draw.circle(
            self.surface,
            PACK_MAN_COLOR,
            (center_x, center_y),
            radius,
        )

        direction = pacman.direction or Direction.RIGHT

        base_angle = {
            Direction.RIGHT: 0,
            Direction.DOWN: 90,
            Direction.LEFT: 180,
            Direction.UP: 270,
        }[direction]

        # Draw eye
        dx, dy = direction.value
        if dx != 0:
            eye_x = center_x + dx * radius // 3
            eye_y = center_y - radius // 3
        else:
            eye_x = center_x + radius // 3
            eye_y = center_y + dy * radius // 3

        pygame.draw.circle(
            self.surface,
            BACKGROUND_COLOR,
            (eye_x, eye_y),
            radius // 5,
        )

        # Mouth opening (degrees)
        if pacman.death_phase > 0:
            if pacman.death_phase >= 0.999:
                pygame.draw.circle(
                    self.surface,
                    BACKGROUND_COLOR,
                    (center_x, center_y),
                    radius,
                )
                return
            opening = 180 * pacman.death_phase
        else:
            opening = 45 * abs(math.sin(pacman.mouth_phase))

        start_angle = base_angle - opening
        end_angle = base_angle + opening

        points = [(center_x, center_y)]

        step = 2

        angle = start_angle
        while angle <= end_angle:
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            points.append((round(x), round(y)))
            angle += step

        # Always include the last point exactly
        rad = math.radians(end_angle)
        x = center_x + radius * math.cos(rad)
        y = center_y + radius * math.sin(rad)
        points.append((round(x), round(y)))

        if len(points) >= 3:
            pygame.draw.polygon(
                self.surface,
                BACKGROUND_COLOR,
                points,
            )

    def _draw_cell(self, row: int, col: int, cell: int) -> None:
        x, y = self._cell_top_left(row, col)
        x = x + self.offset_x
        y = y + self.offset_y

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
        if cell == 15:
            pygame.draw.rect(
                self.surface, "blue",
                (x + WALL_WIDTH // 2,
                 y + WALL_WIDTH // 2,
                 CELL_SIZE,
                 CELL_SIZE))
            return

        center_pos = (x + self.cell_offset, y + self.cell_offset)
        if cell & 32:
            pygame.draw.circle(self.surface, (255, 255, 0), center_pos, 8)
        elif cell & 16:
            pygame.draw.circle(self.surface, (255, 184, 151), center_pos, 3)

    def _draw_title(self, title: str) -> pygame.Rect:
        title_surf = self.title_font.render(
            title, True, ACCENT)
        title_rect = title_surf.get_frect()
        title_rect.centerx = self.center_x
        title_rect.top = int(WINDOW_HEIGHT * _TITLE_Y_FRAC)
        self.surface.blit(title_surf, title_rect)

        # Separator line under title
        sep_y = int(title_rect.bottom + self.line_h * 0.4)
        return pygame.draw.line(
            self.surface, ACCENT, (self.left_x, sep_y),
            (WINDOW_WIDTH - self.left_x, sep_y), 1)

    def _escape_footer(self) -> None:
        footer_surf = self.instruction_font.render(
            "ESC  -  Back to Menu", True, ACCENT)
        footer_rect = footer_surf.get_frect()
        footer_rect.left = self.left_x
        footer_rect.bottom = int(WINDOW_HEIGHT * _FOOTER_BOT_FRAC)
        self.surface.blit(footer_surf, footer_rect)

    def _cell_top_left(self, row: int, col: int) -> Tuple[int, int]:
        return (col * CELL_SIZE, row * CELL_SIZE)
