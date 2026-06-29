from ..scene import Scene
from .final_scene import FinalScene
from .pause_scene import PauseScene
from src.logic import GameLogic
from src.state import Direction, GameState
from ..event import InputEvent
from ..renderer import Renderer


class GameScene(Scene):
    def __init__(self,
                 state: GameState,
                 logic: GameLogic, prev_scene: Scene) -> None:
        super().__init__()
        self.logic = logic
        self.state = state
        self.main_menu = prev_scene

    def update(self, dt: float) -> None:
        if self.state.live_status.lives_remain == 0:
            self.switch_to(
                FinalScene(
                    self.main_menu,
                    self.logic,
                    self.state.live_status.current_score,
                    False))
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
                self.switch_to(PauseScene(self, self.main_menu))
            if event.key == "escape":
                self.switch_to(self.main_menu)

    def render(self, renderer: Renderer) -> None:
        renderer.draw(self.state)
