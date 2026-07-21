from ..scene import Scene
from ..event import InputEvent
from ..renderer import Renderer
from typing import List, Tuple, Any

PLAYERS_PER_PAGE = 96
"""Maximum number of high-score entries displayed on a single page."""


class HighScoresScene(Scene):
    """Scene displaying the complete high-score table.

    Supports paging through the recorded scores and returning to
    the previous scene.
    """
    def __init__(self, prev_scene: Scene,
                 scores: List[Tuple[Any, Any, Any]]) -> None:
        """Initializes the high-scores scene."""
        super().__init__()
        self.prev_scene = prev_scene
        self.scores = scores
        self.scroll = 0

    def handle_event(self, event: InputEvent) -> None:
        """Handles user input.

        Escape returns to the previous scene. Up and down navigate
        between pages of high-score entries.
        """
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
        """Updates the high-scores scene.

        The high-scores scene has no time-dependent behaviour.
        """
        pass

    def render(self, renderer: Renderer) -> None:
        """Draws the current page of high-score entries."""
        renderer.draw_highscores(self.scores, self.scroll)
        self.draw_mobile_controls(renderer.surface)
