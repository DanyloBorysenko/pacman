from ..scene import Scene
from ..event import InputEvent
from ..renderer import Renderer
from ...state import GameConfig


class InstructionsScene(Scene):
    def __init__(self, prev_scene: Scene, config: GameConfig) -> None:
        super().__init__()
        self.prev_scene = prev_scene
        self.config = config

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "keydown":
            if event.key == "escape":
                self.switch_to(self.prev_scene)

    def update(self, dt: float) -> None:
        pass

    def render(self, renderer: Renderer) -> None:
        renderer.draw_instructions(self.config)
        self.draw_mobile_controls(renderer.surface)
