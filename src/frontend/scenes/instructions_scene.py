from ..scene import Scene
from ..event import InputEvent
from ..renderer import Renderer
from ...state import GameConfig


class InstructionsScene(Scene):
    """Scene displaying the game controls and gameplay instructions.

    Shows information loaded from the game configuration and
    returns to the previous scene when requested.
    """
    def __init__(self, prev_scene: Scene, config: GameConfig) -> None:
        """Initializes the instructions scene."""
        super().__init__()
        self.prev_scene = prev_scene
        self.config = config

    def handle_event(self, event: InputEvent) -> None:
        """Handles user input.

        Escape returns to the previous scene.
        """
        if event.type == "keydown":
            if event.key == "escape":
                self.switch_to(self.prev_scene)

    def update(self, dt: float) -> None:
        """Updates the instructions scene.

        The instructions scene has no time-dependent behaviour.
        """
        pass

    def render(self, renderer: Renderer) -> None:
        """Draws the game instructions."""
        renderer.draw_instructions(self.config)
