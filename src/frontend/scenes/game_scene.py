from ..scene import Scene
from src.logic import GameLogic
from src.state import Direction, GameState
from ..event import InputEvent
from ..renderer import Renderer


class GameScene(Scene):
    def __init__(self, state: GameState, logic: GameLogic) -> None:
        super().__init__()
        self.logic = logic
        self.state = state

    def update(self, dt: float) -> None:
        self.logic.update(self.state, dt)

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "quit":
            return
        if event.type == "keydown":
            if event.key == "up" or event.key == "w":
                self.logic.update_direction(self.state, Direction.UP)
            if event.key == "down" or event.key == "s":
                self.logic.update_direction(self.state, Direction.DOWN)
            if event.key == "left" or event.key == "a":
                self.logic.update_direction(self.state, Direction.LEFT)
            if event.key == "right" or event.key == "d":
                self.logic.update_direction(self.state, Direction.RIGHT)
            if event.key == "space":
                self.logic.apply_pause(self.state)
            if event.key == "escape":
                from .main_menu_scene import MainMenuScene
                self.switch_to(MainMenuScene(self.logic))

    def render(self, renderer: Renderer) -> None:
        renderer.draw(self.state)
