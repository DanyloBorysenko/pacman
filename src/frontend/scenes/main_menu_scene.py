from enum import Enum
from ..scene import Scene
from .game_scene import GameScene
from src.logic import GameLogic
from ..event import InputEvent
from ..renderer import Renderer
from typing import List


class MenuItem(Enum):
    START_GAME = "Start Game"
    VIEW_HIGHSCORES = "View Highscores"
    INSTRUCTIONS = "Instructions"
    EXIT = "Exit"


class MainMenuScene(Scene):
    def __init__(self, logic: GameLogic) -> None:
        super().__init__()
        self.logic = logic
        self.selected = 0
        self.items: List[MenuItem] = [
            MenuItem.START_GAME,
            MenuItem.VIEW_HIGHSCORES,
            MenuItem.INSTRUCTIONS,
            MenuItem.EXIT
        ]

    def update(self, dt: float) -> None:
        pass

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "keydown":
            if event.key == "enter":
                state = self.logic.create_default_state()
                self.switch_to(GameScene(state, self.logic))

    def render(self, renderer: Renderer) -> None:
        return renderer.draw_main_menu()
