from abc import ABC, abstractmethod
from .event import InputEvent
from .renderer import Renderer
import pygame
from ..constants import WINDOW_HEIGHT, WINDOW_WIDTH


class Scene(ABC):
    def __init__(self) -> None:
        self._next_scene: "Scene | None" = None

        # --- SHARED VIRTUAL CONTROLLER ---
        self.is_mobile = True  # Toggle for mobile overlays

        # Geometry
        dpad_x, dpad_y = WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100
        btn_sz = 50
        self.touch_up = pygame.Rect(
            dpad_x - btn_sz // 2, dpad_y - btn_sz * 1.5, btn_sz, btn_sz)
        self.touch_down = pygame.Rect(
            dpad_x - btn_sz // 2, dpad_y + btn_sz * 0.5, btn_sz, btn_sz)
        self.touch_left = pygame.Rect(
            dpad_x - btn_sz * 1.5, dpad_y - btn_sz // 2, btn_sz, btn_sz)
        self.touch_right = pygame.Rect(
            dpad_x + btn_sz * 0.5, dpad_y - btn_sz // 2, btn_sz, btn_sz)
        self.touch_enter = pygame.Rect(dpad_x, 20, 70, 40)
        self.touch_back = pygame.Rect(20, 20, 70, 40)

        # Pre-rendered cached surface
        self.controls_overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self._pre_render_mobile_controls()

    def _pre_render_mobile_controls(self) -> None:
        btn_color = (255, 255, 255, 100)
        back_color = (255, 80, 80, 100)

        pygame.draw.rect(
            self.controls_overlay, btn_color,
            self.touch_up, border_radius=5)
        pygame.draw.rect(
            self.controls_overlay, btn_color,
            self.touch_down, border_radius=5)
        pygame.draw.rect(
            self.controls_overlay, btn_color,
            self.touch_left, border_radius=5)
        pygame.draw.rect(
            self.controls_overlay, btn_color,
            self.touch_right, border_radius=5)
        pygame.draw.rect(
            self.controls_overlay, (0, 255, 255, 100),
            self.touch_enter, border_radius=10)
        pygame.draw.rect(
            self.controls_overlay, back_color,
            self.touch_back, border_radius=8)

        font = pygame.font.Font(None, 24)
        for rect, label in [
            (self.touch_up, "▲"), (self.touch_down, "▼"), 
            (self.touch_left, "◀"), (self.touch_right, "▶")
        ]:
            text = font.render(label, True, (255, 255, 255, 180))
            self.controls_overlay.blit(text, text.get_rect(center=rect.center))

        enter_text = font.render("ENTER", True, (255, 255, 255, 220))
        self.controls_overlay.blit(
            enter_text, enter_text.get_rect(center=self.touch_enter.center))

        back_text = font.render("BACK", True, (255, 255, 255, 220))
        self.controls_overlay.blit(
            back_text, back_text.get_rect(center=self.touch_back.center))

    def draw_mobile_controls(self, surface: pygame.Surface) -> None:
        if self.is_mobile:
            surface.blit(self.controls_overlay, (0, 0))

    @abstractmethod
    def handle_event(self, event: InputEvent) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def render(self, renderer: Renderer) -> None:
        pass

    @property
    def next_scene(self) -> "Scene | None":
        scene = self._next_scene
        self._next_scene = None
        return scene

    def switch_to(self, scene: "Scene") -> None:
        self._next_scene = scene
