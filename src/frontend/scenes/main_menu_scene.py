from .models import MenuItem
from ..scene import Scene
from .game_scene import GameScene
from src.backend.logic import GameLogic
from .instructions_scene import InstructionsScene
from .highscores_scene import HighScoresScene
from ..event import InputEvent
from ..renderer import Renderer
from typing import List


class MainMenuScene(Scene):
    """Main menu scene where the player selects how to proceed.

    Displays the available menu options, handles menu navigation,
    shows the top ten high scores, and switches to the selected
    scene when the player confirms a choice.
    """
    def __init__(self, logic: GameLogic) -> None:
        """Initializes the main menu and its available actions."""
        super().__init__()
        self.logic = logic
        self.selected = 0
        self.items: List[str] = [
            MenuItem.START_GAME.value,
            MenuItem.VIEW_HIGHSCORES.value,
            MenuItem.INSTRUCTIONS.value,
            MenuItem.EXIT.value
        ]
        self.run_next_scene = {
            MenuItem.START_GAME.value: self._game_scene,
            MenuItem.EXIT.value: self._exit,
            MenuItem.INSTRUCTIONS.value: self._instruction_scene,
            MenuItem.VIEW_HIGHSCORES.value: self._highscores_scene
        }

    def update(self, dt: float) -> None:
        """Updates the menu state.

        The main menu has no time-dependent behaviour.
        """
        pass

    def handle_event(self, event: InputEvent) -> None:
        """Handles menu navigation and option selection.

        Up and down change the selected menu item. Enter executes
        the action associated with the current selection.
        """
        if event.type == "keydown":
            if event.key == "up":
                self.selected = (self.selected - 1) % len(self.items)
            if event.key == "down":
                self.selected = (self.selected + 1) % len(self.items)
            if event.key == "enter":
                func = self.run_next_scene.get(
                    self.items[self.selected], self._exit)
                func()

    def render(self, renderer: Renderer) -> None:
        """Draws the main menu and the top ten high-score entries."""
        renderer.draw_menu(self.selected, self.items, "Main menu")
        top_players = self.logic.score_board.get_player_list(top_ten=True)
        scores = []
        for i, player in enumerate(top_players):
            scores.append((i+1, player["name"], player["score"]))
        renderer.draw_top_players(scores)
        self.draw_mobile_controls(renderer.surface)

    def _game_scene(self) -> None:
        """Creates a new game and switches to the gameplay scene."""
        state = self.logic.create_default_state()
        self.switch_to(GameScene(state, self.logic, self))

    def _instruction_scene(self) -> None:
        """Switches to the instructions scene."""
        self.switch_to(InstructionsScene(self, self.logic.config))

    def _highscores_scene(self) -> None:
        """Loads all recorded scores and switches to the high-scores scene."""
        top_players = self.logic.score_board.get_player_list(top_ten=False)
        scores = []
        for i, player in enumerate(top_players):
            scores.append((i+1, player["name"], player["score"]))
        self.switch_to(HighScoresScene(self, scores))

    def _exit(self) -> None:
        """Terminates the application."""
        exit()
