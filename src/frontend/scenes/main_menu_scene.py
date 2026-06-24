from ..scene import Scene
from .game_scene import GameScene
from src.logic import GameLogic
from ..event import InputEvent
from ..renderer import Renderer


class MainMenuScene(Scene):
    def __init__(self, logic: GameLogic) -> None:
        super().__init__()
        self.logic = logic

    def update(self, dt: float) -> None:
        pass

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "keydown":
            if event.key == "enter":
                state = self.logic.create_default_state()
                self.switch_to(GameScene(state, self.logic))

    def render(self, renderer: Renderer) -> None:
        return renderer.draw_main_menu()
