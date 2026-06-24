from .renderer import Renderer
from src.logic import GameLogic
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from .scenes.game_scene import GameScene
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
            pygame.K_RETURN: "enter"
        }
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.Clock()
        self.renderer = Renderer(self.screen)
        self.current_scene = MainMenuScene(logic)
        # self.current_scene = GameScene(logic)

    def run(self) -> None:
        self.running = True
        while self.running:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and
                     event.key == pygame.K_ESCAPE)):
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
        if pygame_event.type == pygame.QUIT:
            input_event = InputEvent(type="quit", key=None)
        elif pygame_event.type == pygame.KEYDOWN:
            key = self.events_keys_dict.get(pygame_event.key, None)
            input_event = InputEvent(type="keydown", key=key)
        return input_event
