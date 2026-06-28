from ..scene import Scene
from ...logic import GameLogic
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

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "keydown":
            if event.key == "escape":
                self.switch_to(self.main_menu)
            if event.key == "left":
                self.selected = (self.selected - 1) % len(self.items)
            if event.key == "right":
                self.selected = (self.selected + 1) % len(self.items)
            if event.key == "enter":
                if self.items[self.selected] == "YES":
                    print("Progress was saved")
                    # self.logic.save(self.scores)
                self.switch_to(self.main_menu)

    def update(self, dt: float) -> None:
        pass

    def render(self, renderer: Renderer) -> None:
        if self.is_victory:
            renderer.draw_victory(self.selected)
        else:
            renderer.draw_defeat(self.selected)
