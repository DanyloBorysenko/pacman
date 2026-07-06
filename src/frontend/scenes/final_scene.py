from ..scene import Scene
from ...backend.logic import GameLogic
from ..event import InputEvent
from ..renderer import Renderer


class FinalScene(Scene):
    def __init__(
            self,
            main_menu: Scene,
            logic: GameLogic,
            scores: int,
            is_victory: bool) -> None:
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

    def handle_event(self, event: InputEvent) -> None:
        if self.entering_name:
            if event.type == "keydown" and event.key == "escape":
                self.entering_name = False
            if (event.type == "keydown"
               and event.key == "enter" and self.player_name.strip()):
                self.logic.score_board.add_new_top_player(
                    self.player_name, self.scores)
                self.switch_to(self.main_menu)
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
        pass

    def render(self, renderer: Renderer) -> None:
        if self.is_victory:
            renderer.draw_victory(self.selected)
        else:
            renderer.draw_defeat(self.selected)
        if self.wants_text_input:
            renderer.draw_name_input(self.player_name)

    def set_text_input(self, value: str) -> None:
        self.player_name = value
