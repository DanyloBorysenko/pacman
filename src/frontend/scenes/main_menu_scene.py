from .models import MenuItem
from ..scene import Scene
from .game_scene import GameScene
from .instructions_scene import InstructionsScene
from src.logic import GameLogic
from ..event import InputEvent
from ..renderer import Renderer
from typing import List


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
        self.run_next_scene = {
            MenuItem.START_GAME: self._game_scene,
            MenuItem.EXIT: self._exit,
            MenuItem.INSTRUCTIONS: self._instruction_scene
        }

    def update(self, dt: float) -> None:
        pass

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "keydown":
            if event.key == "up":
                self.selected = (self.selected - 1) % len(self.items)
            if event.key == "down":
                self.selected = (self.selected + 1) % len(self.items)
            if event.key == "enter":
                func = self.run_next_scene.get(
                    self.items[self.selected], self._exit)
                func()

    def render(self, renderer: Renderer) -> None:
        return renderer.draw_main_menu(self.selected, self.items)

    def _game_scene(self) -> None:
        state = self.logic.create_default_state()
        self.switch_to(GameScene(state, self.logic))

    def _instruction_scene(self) -> None:
        self.switch_to(InstructionsScene(self))

    def _exit(self) -> None:
        exit()
