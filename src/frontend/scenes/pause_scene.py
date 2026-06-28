from ..scene import Scene
from ..event import InputEvent
from ..renderer import Renderer
from .models import PauseMenu


class PauseScene(Scene):
    def __init__(self, prev_scene: Scene) -> None:
        super().__init__()
        self.prev_scene = prev_scene
        self.selected = 0
        self.items = [
            PauseMenu.CONTINUE.value,
            PauseMenu.MAIN_MENU.value
        ]

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "keydown":
            if event.key == "escape" or event.key == "space":
                self.switch_to(self.prev_scene)
            if event.key == "up":
                self.selected = (self.selected - 1) % len(self.items)
            if event.key == "down":
                self.selected = (self.selected + 1) % len(self.items)
            if event.key == "enter":
                pass

    def update(self, dt: float) -> None:
        pass

    def render(self, renderer: Renderer) -> None:
        renderer.draw_menu(self.selected, self.items, "Pause")
