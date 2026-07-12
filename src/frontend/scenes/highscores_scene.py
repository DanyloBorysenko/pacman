from ..scene import Scene
from ..event import InputEvent
from ..renderer import Renderer
from typing import List, Tuple

PLAYERS_PER_PAGE = 96


class HighScoresScene(Scene):
    def __init__(self, prev_scene: Scene,
                 scores: List[Tuple[str, str, str]]) -> None:
        super().__init__()
        self.prev_scene = prev_scene
        self.scores = scores
        self.scroll = 0

    def handle_event(self, event: InputEvent) -> None:
        if event.type != "keydown":
            return
        if event.key == "escape":
            self.switch_to(self.prev_scene)
        elif event.key == "down":
            max_page = max(0, (len(self.scores) - 1) // PLAYERS_PER_PAGE)
            self.scroll = min(self.scroll + 1, max_page)
        elif event.key == "up":
            self.scroll = max(0, self.scroll - 1)

    def update(self, dt: float) -> None:
        pass

    def render(self, renderer: Renderer) -> None:
        renderer.draw_highscores(self.scores, self.scroll)
