from abc import ABC, abstractmethod
from .event import InputEvent
from .renderer import Renderer


class Scene(ABC):
    def __init__(self):
        self._next_scene: "Scene | None" = None

    @abstractmethod
    def handle_event(self, event: InputEvent) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def render(self, renderer: Renderer) -> None:
        pass

    @property
    def next_scene(self) -> "Scene | None":
        scene = self._next_scene
        self._next_scene = None
        return scene

    def switch_to(self, scene: "Scene") -> None:
        self._next_scene = scene
