from ..scene import Scene
from ...backend.logic import GameLogic
from ..event import InputEvent
from ..renderer import Renderer

ERR_MSG = "Invalid name! Use max 10 letters, numbers, or spaces."
"""Error message displayed when the entered player name is invalid."""


class FinalScene(Scene):
    """Final scene displayed after a victory or game over.

    Shows the game result, allows the player to save their score,
    and returns to the main menu when finished.
    """
    def __init__(
            self,
            main_menu: Scene,
            logic: GameLogic,
            scores: int,
            is_victory: bool) -> None:
        """Initializes the final scene with the game result and score."""
        super().__init__()
        self.logic = logic
        self.scores = scores
        self.main_menu = main_menu
        self.is_victory = is_victory
        self.items = ["YES", "No"]
        self.selected = 0
        self.entering_name = False
        self.wants_text_input = False
        self.player_name = ""
        self.err_msg: None | str = None

    def handle_event(self, event: InputEvent) -> None:
        """Handles user input.

        Allows the player to choose whether to save their score,
        enter a name, or return to the main menu.
        """
        if self.entering_name:
            if event.type == "keydown" and event.key == "escape":
                self.entering_name = False
            if (event.type == "keydown"
               and event.key == "enter" and self.player_name.strip()):
                added = self.logic.score_board.add_new_player(
                    self.player_name, self.scores)
                if added:
                    self.switch_to(self.main_menu)
                else:
                    self.err_msg = ERR_MSG
                return
        if event.type == "keydown":
            if event.key == "escape":
                self.switch_to(self.main_menu)
            if event.key == "left":
                self.selected = (self.selected - 1) % len(self.items)
            if event.key == "right":
                self.selected = (self.selected + 1) % len(self.items)
            if event.key == "enter":
                if self.items[self.selected] == "YES":
                    self.entering_name = True
                    self.wants_text_input = True
                else:
                    self.switch_to(self.main_menu)

    def update(self, dt: float) -> None:
        """Updates the final scene.

        The final scene has no time-dependent behaviour.
        """
        pass

    def render(self, renderer: Renderer) -> None:
        """Draws the final result screen and, when active, the name
        input dialog."""
        if self.is_victory:
            renderer.draw_victory(self.selected)
        else:
            renderer.draw_defeat(self.selected)
        if self.wants_text_input:
            renderer.draw_name_input(self.player_name, self.err_msg)

    def set_text_input(self, value: str) -> None:
        """Updates the player's entered name."""
        self.player_name = value
