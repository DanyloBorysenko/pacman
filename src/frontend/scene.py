from abc import ABC, abstractmethod
from .event import InputEvent
from .renderer import Renderer


class Scene(ABC):
    """Base class for all game screens (menu, gameplay, victory,
    etc.), following a simple state-machine pattern.

    Subclasses implement handle_event/update/render; switch_to
    queues the next Scene, which the Controller picks up via the
    next_scene property on its following loop iteration.
    """

    def __init__(self) -> None:
        self._next_scene: "Scene | None" = None

    @abstractmethod
    def handle_event(self, event: InputEvent) -> None:
        """React to a single normalized input event."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance scene state by dt seconds."""
        pass

    @abstractmethod
    def render(self, renderer: Renderer) -> None:
        """Draw the current scene state via the given Renderer."""
        pass

    @property
    def next_scene(self) -> "Scene | None":
        """Pops and returns the queued next Scene, if any, clearing
        it so it is only consumed once."""
        scene = self._next_scene
        self._next_scene = None
        return scene

    def switch_to(self, scene: "Scene") -> None:
        """Queues scene as the next active Scene."""
        self._next_scene = scene
