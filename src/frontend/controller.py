from .renderer import Renderer
from src.backend.logic import GameLogic
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from .scenes.main_menu_scene import MainMenuScene
from .event import InputEvent
import pygame


class Controller:
    def __init__(self, logic: GameLogic):
        pygame.init()
        self.events_keys_dict = {
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_SPACE: "space",
            pygame.K_RETURN: "enter",
            pygame.K_i: "i",       # Added for Invincibility cheat toggle
            pygame.K_l: "l",        # Added for Skip Level cheat trigger
            pygame.K_ESCAPE: "escape",
            pygame.K_w: "w",
            pygame.K_a: "a",
            pygame.K_d: "d",
            pygame.K_s: "s",
        }
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.Clock()
        self.renderer = Renderer(self.screen)
        self.current_scene = MainMenuScene(logic)

    def run(self) -> None:
        self.running = True
        while self.running:
            dt = self.clock.tick(120) / 1000
            for event in pygame.event.get():
                if self._should_exit(event):
                    self.running = False
                inp_event = self._to_input_event(event)
                if inp_event is not None:
                    self.current_scene.handle_event(inp_event)
            self.current_scene.update(dt)
            next_scene = self.current_scene.next_scene
            if next_scene:
                self.current_scene = next_scene
            self.screen.fill("black")
            self.current_scene.render(self.renderer)
            pygame.display.update()
        pygame.quit()

    def _to_input_event(self,
                        pygame_event: pygame.event.Event) -> InputEvent | None:
        input_event = None
        if pygame_event.type == pygame.KEYDOWN:
            key = self.events_keys_dict.get(pygame_event.key, None)
            input_event = InputEvent(type="keydown", key=key)
        return input_event

    def _should_exit(self, event: pygame.event.Event) -> bool:
        if (event.type == pygame.QUIT):
            return True
        if (event.type == pygame.KEYDOWN
           and event.key == pygame.K_ESCAPE
           and isinstance(self.current_scene, MainMenuScene)):
            return True
        return False
