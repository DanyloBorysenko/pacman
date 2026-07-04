from ..scene import Scene
from ..event import InputEvent
from ..renderer import Renderer
from typing import List, Tuple


class HighScoresScene(Scene):
    def __init__(self, prev_scene: Scene,
                 scores: List[Tuple[str, str, str]]) -> None:
        super().__init__()
        self.prev_scene = prev_scene
        self.scores = scores

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "keydown":
            if event.key == "escape":
                self.switch_to(self.prev_scene)

    def update(self, dt: float) -> None:
        pass

    def render(self, renderer: Renderer) -> None:
        renderer.draw_highscores(self.scores)
