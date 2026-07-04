from typing import List, Tuple
from src.state import GameState, Direction, Ghost, BitMaps
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
        self.start_game_font = pygame.font.Font(size=200)
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

    def apply_blur(self, factor: int = 8) -> None:
        small = pygame.transform.smoothscale(
            self.surface, (WINDOW_WIDTH // factor, WINDOW_HEIGHT // factor))
        blurred = pygame.transform.smoothscale(small, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.surface.blit(blurred, (0, 0))

    def draw_game_over_text(self, scale: float, alpha: int) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.surface.blit(overlay, (0, 0))

        if scale <= 0.01:
            return
        base_surf = self.title_font.render("GAME OVER", True, "red")
        w, h = base_surf.get_size()
        scaled = pygame.transform.smoothscale(
            base_surf, (max(1, int(w * scale)), max(1, int(h * scale))))
        rect = scaled.get_frect()
        rect.center = (self.center_x, self.center_y)
        self.surface.blit(scaled, rect)

    def draw_confetti(self, particles) -> None:
        for p in particles:
            size = p.size
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(surf, p.color, (0, 0, size, size))
            rotated = pygame.transform.rotate(surf, p.rotation)
            rect = rotated.get_rect(center=(p.x, p.y))
            self.surface.blit(rotated, rect)

    def draw_victory_text(self, scale: float, alpha: int) -> None:
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.surface.blit(overlay, (0, 0))

        if scale <= 0.01:
            return
        base_surf = self.title_font.render("VICTORY!", True, "lime")
        w, h = base_surf.get_size()
        scaled = pygame.transform.smoothscale(
            base_surf, (max(1, int(w * scale)), max(1, int(h * scale))))
        rect = scaled.get_frect()
        rect.center = (self.center_x, self.center_y)
        self.surface.blit(scaled, rect)

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
            # f"Cheat mode:  {'On' if stats.cheat_mode else 'Off'}",
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

    def draw_scores(self, scores: str, x: float, y: float) -> None:
        scores_surf = self.instruction_font.render(scores, True, "ghostwhite")
        scores_rect = scores_surf.get_frect()
        center_x = x * CELL_SIZE + self.offset_x + self.cell_offset
        center_y = y * CELL_SIZE + self.offset_y + self.cell_offset
        scores_rect.center = (center_x, center_y)
        self.surface.blit(scores_surf, scores_rect)

    def draw_ghost(self, ghost: Ghost) -> None:
        center_x = int(ghost.x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(ghost.y * CELL_SIZE + self.offset_y + self.cell_offset)

        radius = CELL_SIZE // 3

        # Temporary surface with transparency
        size = radius * 4
        ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        local_x = size // 2
        local_y = size // 2

        # ----- head -----
        pygame.draw.circle(
            ghost_surface,
            ghost.colour,
            (local_x, local_y - radius // 3),
            radius,
        )

        # ----- body -----
        body = pygame.Rect(
            local_x - radius,
            local_y - radius // 3,
            radius * 2,
            radius + radius // 3,
        )
        pygame.draw.rect(
            ghost_surface,
            ghost.colour,
            body,
        )

        # ----- bottom waves -----
        wave_r = radius // 3
        bottom = body.bottom

        for x in (
            local_x - radius + wave_r,
            local_x,
            local_x + radius - wave_r,
        ):
            pygame.draw.circle(
                ghost_surface,
                ghost.colour,
                (x, bottom),
                wave_r,
            )

        # ----- eyes -----
        eye_w = radius // 2
        eye_h = radius

        left_eye = pygame.Rect(0, 0, eye_w, eye_h)
        left_eye.center = (
            local_x - radius // 3,
            local_y - radius // 2,
        )

        right_eye = pygame.Rect(0, 0, eye_w, eye_h)
        right_eye.center = (
            local_x + radius // 3,
            local_y - radius // 2,
        )

        pygame.draw.ellipse(ghost_surface, "white", left_eye)
        pygame.draw.ellipse(ghost_surface, "white", right_eye)

        pupil = radius // 6

        dx, dy = ghost.assigned_direction
        offset = radius // 8

        pygame.draw.circle(
            ghost_surface,
            "blue",
            (
                left_eye.centerx + dx * offset,
                left_eye.centery + dy * offset,
            ),
            pupil,
        )

        pygame.draw.circle(
            ghost_surface,
            "blue",
            (
                right_eye.centerx + dx * offset,
                right_eye.centery + dy * offset,
            ),
            pupil,
        )

        # Apply transparency
        ghost_surface.set_alpha(int(255 * ghost.alpha))

        # Draw on screen
        self.surface.blit(
            ghost_surface,
            (
                center_x - local_x,
                center_y - local_y,
            ),
        )

    def draw_edible_ghost(self, ghost: Ghost) -> None:
        center_x = int(ghost.x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(ghost.y * CELL_SIZE + self.offset_y + self.cell_offset)

        radius = CELL_SIZE // 3

        # Temporary surface with transparency
        size = radius * 4
        ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        local_x = size // 2
        local_y = size // 2

        # ----- head -----
        pygame.draw.circle(
            ghost_surface,
            ghost.colour,
            (local_x, local_y - radius // 3),
            radius,
        )

        # ----- body -----
        body = pygame.Rect(
            local_x - radius,
            local_y - radius // 3,
            radius * 2,
            radius + radius // 3,
        )
        pygame.draw.rect(
            ghost_surface,
            ghost.colour,
            body,
        )

        # ----- bottom waves -----
        wave_r = radius // 3
        bottom = body.bottom

        for x in (
            local_x - radius + wave_r,
            local_x,
            local_x + radius - wave_r,
        ):
            pygame.draw.circle(
                ghost_surface,
                ghost.colour,
                (x, bottom),
                wave_r,
            )

        # ----- eyes -----
        eye_size = radius // 5

        left_eye = pygame.Rect(0, 0, eye_size, eye_size)
        left_eye.center = (
            local_x - radius // 3,
            local_y - radius // 2,
        )

        right_eye = pygame.Rect(0, 0, eye_size, eye_size)
        right_eye.center = (
            local_x + radius // 3,
            local_y - radius // 2,
        )

        pygame.draw.circle(ghost_surface, "white", left_eye.center, eye_size)
        pygame.draw.circle(ghost_surface, "white", right_eye.center, eye_size)

        # ----- mouth -----
        mouth_y = left_eye.bottom + radius // 2
        mouth_left = left_eye.left
        mouth_right = right_eye.right
        points = []
        num_points = 40
        waves = 2.5
        amplitude = radius / 14

        for i in range(num_points):
            t = i / (num_points - 1)
            x = mouth_left + t * (mouth_right - mouth_left)
            y = mouth_y + math.sin(t * math.pi * waves) * amplitude
            points.append((x, y))

        pygame.draw.aalines(ghost_surface, "white", False, points)

        # Apply transparency
        ghost_surface.set_alpha(int(255 * ghost.alpha))

        # Draw on screen
        self.surface.blit(
            ghost_surface,
            (
                center_x - local_x,
                center_y - local_y,
            ),
        )

    def draw_start(self, scale: float, text: str) -> None:
        if scale <= 0.01:
            return
        base_surf = self.start_game_font.render(text, True, "red")
        w, h = base_surf.get_size()
        scaled = pygame.transform.smoothscale(
            base_surf, (max(1, int(w * scale)), max(1, int(h * scale))))
        rect = scaled.get_frect()
        rect.center = (self.center_x, self.center_y)
        self.surface.blit(scaled, rect)

    def _draw_gosts(self) -> None:
        for ghost in self.state.ghosts:
            if ghost.is_edible:
                self.draw_edible_ghost(ghost)
            else:
                self.draw_ghost(ghost)

    def _draw_pacman(self) -> None:
        pacman = self.state.pacman
        if pacman.death_phase > 0:
            return  # death animation handles drawing instead

        center_x = int(pacman.x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(pacman.y * CELL_SIZE + self.offset_y + self.cell_offset)
        radius = CELL_SIZE // 3

        pygame.draw.circle(self.surface, PACK_MAN_COLOR, (center_x, center_y), radius)

        direction = pacman.direction or Direction.RIGHT
        base_angle = {
            Direction.RIGHT: 0,
            Direction.DOWN: 90,
            Direction.LEFT: 180,
            Direction.UP: 270,
        }[direction]

        dx, dy = direction.value
        if dx != 0:
            eye_x = center_x + dx * radius // 3
            eye_y = center_y - radius // 3
        else:
            eye_x = center_x + radius // 3
            eye_y = center_y + dy * radius // 3

        pygame.draw.circle(self.surface, BACKGROUND_COLOR, (eye_x, eye_y), radius // 5)

        opening = 45 * abs(math.sin(pacman.mouth_phase))
        start_angle = base_angle - opening
        end_angle = base_angle + opening

        points = [(center_x, center_y)]
        step = 2
        angle = start_angle
        while angle <= end_angle:
            rad = math.radians(angle)
            points.append((
                round(center_x + radius * math.cos(rad)),
                round(center_y + radius * math.sin(rad)),
            ))
            angle += step

        rad = math.radians(end_angle)
        points.append((
            round(center_x + radius * math.cos(rad)),
            round(center_y + radius * math.sin(rad)),
        ))

        if len(points) >= 3:
            pygame.draw.polygon(self.surface, BACKGROUND_COLOR, points)

    def draw_pacman_death(self, x: float, y: float, death_phase: float) -> None:
        center_x = int(x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(y * CELL_SIZE + self.offset_y + self.cell_offset)
        radius = CELL_SIZE // 3

        if death_phase >= 0.999:
            return  # fully closed — nothing left to draw

        opening = 180 * death_phase
        start_angle = -opening
        end_angle = opening

        pygame.draw.circle(self.surface, PACK_MAN_COLOR, (center_x, center_y), radius)

        points = [(center_x, center_y)]
        step = 2
        angle = start_angle
        while angle <= end_angle:
            rad = math.radians(angle)
            points.append((
                round(center_x + radius * math.cos(rad)),
                round(center_y + radius * math.sin(rad)),
            ))
            angle += step

        rad = math.radians(end_angle)
        points.append((
            round(center_x + radius * math.cos(rad)),
            round(center_y + radius * math.sin(rad)),
        ))

        if len(points) >= 3:
            pygame.draw.polygon(self.surface, BACKGROUND_COLOR, points)

    def draw_pacman_explosion(self, x: float, y: float, particles) -> None:
        center_x = x * CELL_SIZE + self.offset_x + self.cell_offset
        center_y = y * CELL_SIZE + self.offset_y + self.cell_offset
        for p in particles:
            x = int(center_x + p.dx * CELL_SIZE)
            y = int(center_y + p.dy * CELL_SIZE)
            pygame.draw.circle(self.surface, p.color, (x, y), max(1, int(p.size)))

    def _draw_cell(self, row: int, col: int, cell: int) -> None:
        x, y = self._cell_top_left(row, col)
        x = x + self.offset_x
        y = y + self.offset_y

        if cell & BitMaps.NORTH:
            pygame.draw.line(
                self.surface, MAZE_COLOR,
                (x, y), (x + CELL_SIZE, y), WALL_WIDTH)
        if cell & BitMaps.EAST:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x + CELL_SIZE, y),
                (x + CELL_SIZE, y + CELL_SIZE), WALL_WIDTH)
        if cell & BitMaps.SOUTH:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y + CELL_SIZE),
                (x + CELL_SIZE, y + CELL_SIZE), WALL_WIDTH)
        if cell & BitMaps.WEST:
            pygame.draw.line(
                self.surface, MAZE_COLOR, (x, y),
                (x, y + CELL_SIZE), WALL_WIDTH)
        if cell == BitMaps.WALL_MASK.value:
            pygame.draw.rect(
                self.surface, "blue",
                (x + WALL_WIDTH // 2,
                 y + WALL_WIDTH // 2,
                 CELL_SIZE,
                 CELL_SIZE))
            return

        center_pos = (x + self.cell_offset, y + self.cell_offset)
        if cell & BitMaps.SUPER_PACGUM.value:
            pygame.draw.circle(self.surface, (255, 255, 0), center_pos, 8)
        elif cell & BitMaps.PACGUM.value:
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
