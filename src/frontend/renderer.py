from typing import List, Tuple, Any
from src.state import GameState, Direction, Ghost, BitMaps, GameConfig
from src.constants import CELL_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
from dataclasses import replace
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

BLINK_WINDOW = 2.0

WALL_WIDTH = 5

# ── Layout constants (all relative to surface size) ──────────────────────────
_TITLE_Y_FRAC = 0.04   # title top edge as fraction of height
_BODY_TOP_FRAC = 0.14   # where columns start
_COL_LEFT_FRAC = 0.04   # left column x
_COL_RIGHT_FRAC = 0.52   # right column x
_LINE_H_FRAC = 0.038  # vertical step between lines
_FOOTER_BOT_FRAC = 0.97   # footer bottom edge

DIRECTION_ANGLES = {
    Direction.RIGHT: 0,
    Direction.DOWN: 90,
    Direction.LEFT: 180,
    Direction.UP: 270,
}


class Renderer:
    """Draws all game visuals onto a pygame Surface: menus,
    instructions, highscores, the maze, HUD, Pac-Man, ghosts, and
    transition/overlay effects. Stateless between frames aside from
    cached fonts, images, and layout offsets."""

    def __init__(
            self,
            surface: pygame.Surface) -> None:
        """Loads fonts and sprite assets and precomputes layout
        offsets for the given render target surface."""
        self.surface = surface
        self.menu_font = pygame.font.Font(size=MENU_FONT_SIZE)
        self.title_font = pygame.font.Font(None, 50)
        self.instruction_font = pygame.font.Font(
            "assets/fonts/DejaVuSans.ttf", 20)
        self.start_game_font = pygame.font.Font(size=200)
        self.top_players_tittle_font = pygame.font.Font(
            size=MENU_FONT_SIZE // 2)
        self.top_players_font = pygame.font.Font(size=MENU_FONT_SIZE // 3)
        self.offset_x = 0
        self.offset_y = 0
        self.cell_offset = CELL_SIZE // 2
        self.center_x = WINDOW_WIDTH // 2
        self.center_y = WINDOW_HEIGHT // 2
        self.line_h = int(WINDOW_HEIGHT * _LINE_H_FRAC)
        self.left_x = int(WINDOW_WIDTH * _COL_LEFT_FRAC)

        self.cherry_image = pygame.image.load(
            "assets/images/cherry_b.png").convert_alpha()
        self.cherry_image = pygame.transform.smoothscale(
            self.cherry_image, (int(CELL_SIZE), int(CELL_SIZE))
        )

    def draw_menu(self,
                  sel_item: int,
                  items: List[str],
                  title: str) -> None:
        """Draws a titled vertical menu list, highlighting the
        item at index sel_item."""
        title_rect = self._draw_title(title)
        self.menu_title_bottom = title_rect.bottom
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

    def draw_top_players(self,
                         data: List[Tuple[Any, Any, Any]]) -> None:
        """Renders a compact top-10 (place, name, score) list below
        the menu title, used on the main menu screen."""
        top_players_surf = self.top_players_tittle_font.render(
            "Top 10 players:", True, (150, 150, 150))
        top_players_rect = top_players_surf.get_frect()
        top_players_rect.topleft = (self.left_x, self.menu_title_bottom + 20)
        self.surface.blit(top_players_surf, top_players_rect)
        spacing = 5
        current_y = top_players_rect.bottom + spacing * 2
        for line in data:
            place, name, score = line
            player_surf = self.top_players_font.render(
                f"{place}    {name}    {score}", True, (150, 150, 150)
            )
            player_rect = player_surf.get_frect()
            player_rect.left = top_players_rect.left
            player_rect.top = current_y
            self.surface.blit(player_surf, player_rect)
            current_y += player_rect.height + spacing

    def draw_instructions(self, config: GameConfig) -> None:
        """Draws the two-column instructions/help screen (controls,
        pacgums, ghosts, gameplay, winning), populated with values
        from the current GameConfig."""
        right_x = int(WINDOW_WIDTH * _COL_RIGHT_FRAC)
        body_top = int(WINDOW_HEIGHT * _BODY_TOP_FRAC)

        # ── Helpers ──
        def build_text(text: str, x: int, y: int,
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
                    build_text(text, x, y, color)
                y += self.line_h

        blank = ("", INSTRUCTION_COLOR)      # empty-line sentinel

        left_column: list[tuple[str, str]] = [
            ("Controls",                    ACCENT),
            ("\u2191 / W    Move Up",        INSTRUCTION_COLOR),
            ("\u2193 / S    Move Down",      INSTRUCTION_COLOR),
            ("\u2190 / A    Move Left",      INSTRUCTION_COLOR),
            ("\u2192 / D    Move Right",     INSTRUCTION_COLOR),
            ("Space      Pause",             INSTRUCTION_COLOR),
            blank,
            ("Pacgums",                      ACCENT),
            (f"\u2022 Pacgum          +{config.points_per_pacgum} pts",
                INSTRUCTION_COLOR),
            (f"\u2022 Super Pacgum    +{config.points_per_super_pacgum} pts",
                INSTRUCTION_COLOR),
            blank,
            ("Ghosts",                      ACCENT),
            (f"\u2022 Ghost          +{config.points_per_ghost} pts",
                INSTRUCTION_COLOR),
            (f"\u2022 Frightens ghosts for {config.ghost_edible_time} seconds",
                INSTRUCTION_COLOR)
        ]

        right_column: list[tuple[str, str]] = [
            ("Gameplay",                            ACCENT),
            (f"\u2022 Start with {config.lives} lives",
                INSTRUCTION_COLOR),
            ("\u2022 Move only through corridors",   INSTRUCTION_COLOR),
            ("\u2022 Walls block movement",          INSTRUCTION_COLOR),
            ("\u2022 Touching a ghost loses a life", INSTRUCTION_COLOR),
            ("\u2022 Respawn in maze center",        INSTRUCTION_COLOR),
            ("\u2022 Game Over at 0 lives",          INSTRUCTION_COLOR),
            ("\u2022 Finish level by eating every pacgum", INSTRUCTION_COLOR),
            ("\u2022 Increase lifes by eating cherry", INSTRUCTION_COLOR),
            blank,
            ("Ghosts",                               ACCENT),
            ("\u2022 Chase Pac-Man",                 INSTRUCTION_COLOR),
            ("\u2022 Run away when edible",          INSTRUCTION_COLOR),
            (f"\u2022 Respawn after {config.ghost_reappear_time} sec",
                INSTRUCTION_COLOR),
            blank,
            ("Winning",                      ACCENT),
            (f"\u2022 Complete {config.max_level} levels", INSTRUCTION_COLOR),
            ("\u2022 Eat every pacgum",      INSTRUCTION_COLOR),
        ]

        self._draw_title("PAC-MAN INSTRUCTIONS")

        # ── Columns ──
        draw_column(left_column,  self.left_x,  body_top)
        draw_column(right_column, right_x, body_top)

        self._escape_footer()

    def draw_highscores(
        self, data: List[Tuple[str, str, str]],
            scroll: int = 0) -> None:
        """Draws a paginated, multi-column highscores table for
        the given scroll page (up to 4 columns per page)."""
        title_rect = self._draw_title("Highscores")

        if not data:
            self._escape_footer()
            return

        font = self.top_players_tittle_font
        font_height = font.get_height()

        vertical_spacing = 6
        horizontal_margin = 20

        available_height = (
            WINDOW_HEIGHT
            - title_rect.bottom
            - 50
        )

        rows = max(
            1,
            available_height // (font_height + vertical_spacing)
        )

        # Fixed number of columns per page.
        columns = 4
        page_size = rows * columns

        max_page = max(0, (len(data) - 1) // page_size)
        scroll = max(0, min(scroll, max_page))

        start = scroll * page_size
        page = data[start:start + page_size]

        # The last page may contain fewer than 4 columns.
        page_columns = max(1, (len(page) + rows - 1) // rows)

        usable_width = WINDOW_WIDTH - horizontal_margin * 2
        column_width = usable_width // page_columns

        start_x = horizontal_margin

        total_height = (
            rows * font_height +
            (rows - 1) * vertical_spacing
        )

        start_y = title_rect.bottom + (
            available_height - total_height
        ) // 2

        for index, (place, name, score) in enumerate(page):

            column = index // rows
            row = index % rows

            text = f"{int(place):>3}. {name[:10]:<10} {int(score):>6}"

            surf = font.render(text, True, "white")
            rect = surf.get_rect()

            rect.x = (
                start_x
                + column * column_width
                + 5
            )

            rect.y = (
                start_y
                + row * (font_height + vertical_spacing)
            )

            self.surface.blit(surf, rect)

        self._escape_footer()

    def draw(self, state: GameState) -> None:
        """Renders one full gameplay frame: maze, HUD stats,
        Pac-Man, and ghosts, centering the maze on the surface."""
        self.state = state
        maze_width = CELL_SIZE * len(state.maze[0])
        maze_height = CELL_SIZE * len(state.maze)
        self.offset_x = (WINDOW_WIDTH - maze_width) // 2
        self.offset_y = (WINDOW_HEIGHT - maze_height) // 2
        self._draw_maze()
        self._draw_game_stats()
        self._draw_pacman()
        self._draw_ghosts()

    def draw_victory(self, sel_item: int) -> None:
        """Draws the victory result screen."""
        self._draw_game_result("You Win!", "green", sel_item)

    def draw_defeat(self, sel_item: int) -> None:
        """Draws the game-over result screen."""
        self._draw_game_result("Game Over", "red", sel_item)

    def _draw_game_result(
        self,
        title: str,
        color: str,
        sel_item: int,
    ) -> None:
        """Shared layout for the victory/defeat screens: title,
        final score, and the save-result yes/no question menu."""
        self._escape_footer()

        title_surf = self.menu_font.render(title, True, color)
        title_rect = title_surf.get_frect()
        title_rect.center = (self.center_x, PADDING * 2)
        self.surface.blit(title_surf, title_rect)

        score_surf = self.title_font.render(
            f"Score: {self.state.live_status.current_score}",
            True,
            "white",
        )
        score_rect = score_surf.get_frect()
        score_rect.top = title_rect.bottom + PADDING
        score_rect.centerx = title_rect.centerx
        self.surface.blit(score_surf, score_rect)

        self._draw_question_menu(sel_item)

    def apply_blur(self, factor: int = 8) -> None:
        """Applies a cheap box-blur to the surface by downscaling
        then upscaling by factor, used behind pause/overlay text."""
        small = pygame.transform.smoothscale(
            self.surface, (WINDOW_WIDTH // factor, WINDOW_HEIGHT // factor))
        blurred = pygame.transform.smoothscale(
            small, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.surface.blit(blurred, (0, 0))

    def draw_game_over_text(self, scale: float, alpha: int) -> None:
        """Draws a darkening overlay plus a scaling "GAME OVER"
        title, for the death animation sequence."""
        overlay = pygame.Surface((
            WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
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

    def draw_level_up_text(self, scale: float, text: str, alpha: int) -> None:
        """Draws a darkening overlay plus a scaling level-up
        message, for the level transition sequence."""
        overlay = pygame.Surface((
            WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.surface.blit(overlay, (0, 0))

        if scale <= 0.01:
            return
        base_surf = self.title_font.render(text, True, "cyan")
        w, h = base_surf.get_size()

        scaled = pygame.transform.smoothscale(
            base_surf, (max(1, int(w * scale)), max(1, int(h * scale))))

        rect = scaled.get_frect()
        rect.center = (self.center_x, self.center_y)
        self.surface.blit(scaled, rect)

    def draw_confetti(self, particles: Any) -> None:
        """Draws a burst of small rotated rectangle particles,
        used as a victory celebration effect."""
        for p in particles:
            size = p.size
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(surf, p.color, (0, 0, size, size))
            rotated = pygame.transform.rotate(surf, p.rotation)
            rect = rotated.get_rect(center=(p.x, p.y))
            self.surface.blit(rotated, rect)

    def draw_victory_text(self, scale: float, alpha: int) -> None:
        """Draws a darkening overlay plus a scaling "VICTORY!"
        title, for the level-clear animation sequence."""
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
        """Draws the "save your result?" Yes/No button pair,
        highlighting the currently selected option."""
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

    def draw_name_input(self, name: str, msg: None | str) -> None:
        """Draws the highscore name-entry text box, its prompt
        label, and an optional validation error message."""
        box_w, box_h = 400, 70
        box = pygame.Rect(0, 0, box_w, box_h)
        box.center = (self.center_x, self.center_y + WINDOW_HEIGHT // 4)

        pygame.draw.rect(
            self.surface, pygame.Color(30, 30, 30), box, border_radius=8)
        pygame.draw.rect(self.surface, ACCENT, box, width=2, border_radius=8)
        name_size = box_h // 2
        surf = pygame.font.Font(size=box_h // 2).render(name, True, "white")
        text_rect = surf.get_frect()
        text_rect.center = box.center
        self.surface.blit(surf, text_rect)

        info_surf = pygame.font.Font(size=name_size).render(
            "Please write your name", True, (50, 50, 50))
        info_rect = info_surf.get_frect()
        info_rect.bottom = box.top - 5
        info_rect.centerx = box.centerx
        self.surface.blit(info_surf, info_rect)
        if msg:
            err_surf = pygame.font.Font(size=name_size).render(
                msg, True, "red")
            err_rect = err_surf.get_frect()
            err_rect.top = box.bottom + 10
            err_rect.centerx = box.centerx
            self.surface.blit(err_surf, err_rect)

    def _draw_game_stats(self) -> None:
        """Draws the in-game HUD: score, level, lives, and
        remaining time if the level has a time limit."""
        stats = self.state.live_status

        center_y = WINDOW_HEIGHT // 2
        spacing = 40

        items = [
            f"Score:  {stats.current_score}",
            f"Level:  {stats.current_level}",
            f"Lives:  {stats.lives_remain}"
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
                f"Time: {int(stats.time_left)}",
                True,
                PACK_MAN_COLOR,
            )
            rect = surf.get_frect()
            rect.left = PADDING
            rect.bottom = WINDOW_HEIGHT - PADDING
            self.surface.blit(surf, rect)

    def _draw_maze(self) -> None:
        """Draws every maze cell (walls and collectibles) by
        iterating the current state's maze grid."""
        for row, line in enumerate(self.state.maze):
            for col, cell in enumerate(line):
                self._draw_cell(row, col, cell)

    def draw_scores(self, scores: str, x: float, y: float) -> None:
        """Draws a floating score-popup label centered on the
        given maze grid coordinate."""
        scores_surf = self.instruction_font.render(scores, True, "ghostwhite")
        scores_rect = scores_surf.get_frect()
        center_x = x * CELL_SIZE + self.offset_x + self.cell_offset
        center_y = y * CELL_SIZE + self.offset_y + self.cell_offset
        scores_rect.center = (center_x, center_y)
        self.surface.blit(scores_surf, scores_rect)

    def draw_ghost(self, ghost: Ghost) -> None:
        """Draws a single ghost sprite (head, body, wavy bottom,
        and face) at its current position, applying its alpha."""
        if not ghost.colour:
            return

        center_x = int(ghost.x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(ghost.y * CELL_SIZE + self.offset_y + self.cell_offset)

        radius = CELL_SIZE // 3
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

        if ghost.is_edible:
            self._draw_edible_face(
                ghost_surface,
                local_x,
                local_y,
                radius,
            )
        else:
            self._draw_normal_face(
                ghost_surface,
                ghost,
                local_x,
                local_y,
                radius,
            )

        ghost_surface.set_alpha(int(255 * ghost.alpha))

        self.surface.blit(
            ghost_surface,
            (
                center_x - local_x,
                center_y - local_y,
            ),
        )

    def _draw_normal_face(
        self,
        surface: pygame.Surface,
        ghost: Ghost,
        center_x: int,
        center_y: int,
        radius: int,
    ) -> None:
        """Draws a ghost's normal eyes, with pupils offset toward
        its assigned_direction."""
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

        pygame.draw.ellipse(surface, "white", left_eye)
        pygame.draw.ellipse(surface, "white", right_eye)

        pupil = radius // 6
        offset = radius // 8

        dx, dy = ghost.assigned_direction

        pygame.draw.circle(
            surface,
            "blue",
            (
                left_eye.centerx + dx * offset,
                left_eye.centery + dy * offset,
            ),
            pupil,
        )

        pygame.draw.circle(
            surface,
            "blue",
            (
                right_eye.centerx + dx * offset,
                right_eye.centery + dy * offset,
            ),
            pupil,
        )

    def _draw_edible_face(
        self,
        surface: pygame.Surface,
        center_x: int,
        center_y: int,
        radius: int,
    ) -> None:
        """Draws a frightened/edible ghost's face: small round eyes
        and a wavy sine-curve mouth."""
        eye_size = radius // 5

        left_eye = pygame.Rect(0, 0, eye_size, eye_size)
        left_eye.center = (
            center_x - radius // 3,
            center_y - radius // 2,
        )

        right_eye = pygame.Rect(0, 0, eye_size, eye_size)
        right_eye.center = (
            center_x + radius // 3,
            center_y - radius // 2,
        )

        pygame.draw.circle(surface, "white", left_eye.center, eye_size)
        pygame.draw.circle(surface, "white", right_eye.center, eye_size)

        mouth_y = left_eye.bottom + radius // 2
        mouth_left = left_eye.left
        mouth_right = right_eye.right

        points = []

        for i in range(40):
            t = i / 39
            x = int(mouth_left + t * (mouth_right - mouth_left))
            y = mouth_y + math.sin(t * math.pi * 2.5) * radius / 14
            points.append((x, y))

        pygame.draw.aalines(surface, "white", False, points)

    def _draw_ghosts(self) -> None:
        """Draws all live ghosts, blinking edible ghosts back to
        their normal color as their frightened time runs out."""
        config = self.state.config

        for ghost in self.state.ghosts:
            if ghost.is_dead:
                continue

            if not ghost.is_edible:
                self.draw_ghost(ghost)
                continue

            remaining = config.ghost_edible_time - ghost.time_laps

            if remaining > BLINK_WINDOW:
                self.draw_ghost(ghost)
                continue

            if int(ghost.time_laps / 0.2) % 2 == 0:
                self.draw_ghost(ghost)
            else:
                self.draw_ghost(replace(
                    ghost, colour=ghost.initial_colour, is_edible=False))

    def draw_start(self, scale: float, text: str) -> None:
        """Draws a large scaling countdown/start text, e.g. for a
        "READY?" or "3-2-1" intro animation."""
        if scale <= 0.01:
            return
        base_surf = self.start_game_font.render(text, True, "red")
        w, h = base_surf.get_size()
        scaled = pygame.transform.smoothscale(
            base_surf, (max(1, int(w * scale)), max(1, int(h * scale))))
        rect = scaled.get_frect()
        rect.center = (self.center_x, self.center_y)
        self.surface.blit(scaled, rect)

    def _draw_pacman(self) -> None:
        """Draws Pac-Man at his current position with an animated
        chomping mouth, unless mid-death animation."""
        pacman = self.state.pacman
        if pacman.death_phase > 0:
            return

        opening = 45 * abs(math.sin(pacman.mouth_phase))

        self._draw_pacman_shape(
            pacman.x,
            pacman.y,
            pacman.direction or Direction.RIGHT,
            opening,
            True,
        )

    def draw_pacman_death(
        self,
        x: float,
        y: float,
        direction: Direction,
        death_phase: float,
    ) -> None:
        """Draws Pac-Man's death animation: his mouth opens wider
        as death_phase progresses from 0 to 1."""
        if death_phase >= 0.999:
            return

        self._draw_pacman_shape(
            x,
            y,
            direction,
            180 * death_phase,
            False,
        )

    def _draw_pacman_shape(
        self,
        x: float,
        y: float,
        direction: Direction,
        opening: float,
        draw_eye: bool,
    ) -> None:
        """Draws the Pac-Man circle-with-wedge-mouth shape at a
        maze coordinate, facing direction, with the mouth opened
        by opening degrees on each side and an optional eye."""
        center_x = int(x * CELL_SIZE + self.offset_x + self.cell_offset)
        center_y = int(y * CELL_SIZE + self.offset_y + self.cell_offset)
        radius = CELL_SIZE // 3

        pygame.draw.circle(
            self.surface,
            PACK_MAN_COLOR,
            (center_x, center_y),
            radius,
        )

        base_angle = {
            Direction.RIGHT: 0,
            Direction.DOWN: 90,
            Direction.LEFT: 180,
            Direction.UP: 270,
        }[direction]

        if draw_eye:
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

        pygame.draw.polygon(
            self.surface,
            BACKGROUND_COLOR,
            points,
        )

    def draw_pacman_explosion(self, x: float, y: float, particles: Any
                              ) -> None:
        """Draws Pac-Man's death explosion particles radiating from
        his last maze position."""
        center_x = x * CELL_SIZE + self.offset_x + self.cell_offset
        center_y = y * CELL_SIZE + self.offset_y + self.cell_offset
        for p in particles:
            x = int(center_x + p.dx * CELL_SIZE)
            y = int(center_y + p.dy * CELL_SIZE)
            pygame.draw.circle(
                self.surface, p.color, (x, y), max(1, int(p.size)))

    def _draw_cell(self, row: int, col: int, cell: int) -> None:
        """Draws a single maze cell's walls (per BitMaps flags) or
        solid wall block, and any collectible it contains."""
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
        elif cell & BitMaps.CHERRY.value:
            cherry_rect = self.cherry_image.get_frect()
            cherry_rect.center = center_pos
            self.surface.blit(self.cherry_image, cherry_rect)

    def _draw_title(self, title: str) -> pygame.Rect:
        """Draws a centered screen title with a separator line
        below it, returning the separator's Rect for layout."""
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
        """Draws the "ESC - Back to Menu" footer hint used on
        instructions/highscores screens."""
        footer_surf = self.instruction_font.render(
            "ESC  -  Back to Menu", True, ACCENT)
        footer_rect = footer_surf.get_frect()
        footer_rect.left = self.left_x
        footer_rect.bottom = int(WINDOW_HEIGHT * _FOOTER_BOT_FRAC)
        self.surface.blit(footer_surf, footer_rect)

    def _cell_top_left(self, row: int, col: int) -> Tuple[int, int]:
        """Converts a (row, col) maze index to its top-left pixel
        offset within the maze (before centering offsets)."""
        return (col * CELL_SIZE, row * CELL_SIZE)
