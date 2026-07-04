from ..scene import Scene
from src.backend.logic import GameLogic
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
            if event.key == "up":
                self.logic.update_direction(self.state, Direction.UP)
            if event.key == "down":
                self.logic.update_direction(self.state, Direction.DOWN)
            if event.key == "left":
                self.logic.update_direction(self.state, Direction.LEFT)
            if event.key == "right":
                self.logic.update_direction(self.state, Direction.RIGHT)
            if event.key == "space":
                self.logic.apply_pause(self.state)

            # --- CHEAT MODE KEY ROUTING ---
            if event.key == "i":
                self.logic.toggle_invincibility(self.state)
            if event.key == "l":
                self.logic.cheat_skip_level(self.state)

    def render(self, renderer: Renderer) -> None:
        renderer.draw(self.state)
