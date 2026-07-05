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
    def __init__(self, logic: GameLogic) -> None:
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
        pass

    def handle_event(self, event: InputEvent) -> None:
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
        return renderer.draw_menu(self.selected, self.items, "Main menu")

    def _game_scene(self) -> None:
        state = self.logic.create_default_state()
        # state.events.append(GameStartEvent())
        self.switch_to(GameScene(state, self.logic, self))

    def _instruction_scene(self) -> None:
        self.switch_to(InstructionsScene(self))

    def _highscores_scene(self) -> None:
        top_players = self.logic.score_board.get_player_list()
        scores = []
        for i, player in enumerate(top_players):
            scores.append((i+1, player["name"], player["score"]))
        self.switch_to(HighScoresScene(self, scores))

    def _exit(self) -> None:
        exit()
