from __future__ import annotations
from typing import Callable
from ..scene import Scene
from ..event import InputEvent
from ..renderer import Renderer
from .models import PauseMenu


class PauseScene(Scene):
    """Pause menu displayed while gameplay is temporarily suspended.

    Allows the player to resume the current game or return to the
    main menu.
    """
    def __init__(self, prev_scene: Scene, main_menu: Scene,
                 chasing_sound: Callable) -> None:
        """Initializes the pause menu and its available actions."""
        super().__init__()
        self.prev_scene = prev_scene
        self.selected = 0
        self.items = [
            PauseMenu.CONTINUE.value,
            PauseMenu.MAIN_MENU.value
        ]
        self.main_menu = main_menu
        self.chasing_sound = chasing_sound

    def _resume_game(self) -> None:
        """Centralizes audio resumption rules and returns to the game screen."""
        self.chasing_sound.play(loops=-1)
        self.switch_to(self.prev_scene)

    def handle_event(self, event: InputEvent) -> None:
        """Handles menu navigation and option selection.

        Escape or Space resumes the game. Up and down change the
        selected menu item, and Enter executes the selected action.
        """
        if event.type == "keydown":
            if event.key == "escape" or event.key == "space":
                self._resume_game()
            if event.key == "up":
                self.selected = (self.selected - 1) % len(self.items)
            if event.key == "down":
                self.selected = (self.selected + 1) % len(self.items)
            if event.key == "enter":
                if self.items[self.selected] == PauseMenu.CONTINUE.value:
                    self._resume_game()
                elif self.items[self.selected] == PauseMenu.MAIN_MENU.value:
                    self.switch_to(self.main_menu)

    def update(self, dt: float) -> None:
        """Updates the pause menu state.

        The pause menu has no time-dependent behaviour.
        """
        pass

    def render(self, renderer: Renderer) -> None:
        """Draws the pause menu."""
        renderer.draw_menu(self.selected, self.items, "Pause")
