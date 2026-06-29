from ..scene import Scene
from .final_scene import FinalScene
from .pause_scene import PauseScene
from src.logic import GameLogic
from src.state import Direction, GameState, GameOverEvent, VictoryEvent
from ..event import InputEvent
from ..renderer import Renderer
from typing import List
from abc import ABC, abstractmethod


class Animation(ABC):
    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @property
    @abstractmethod
    def finished(self) -> bool:
        pass


class AnimationManager:
    def __init__(self):
        self._animations: List[Animation] = []

    def add(self, animation: Animation) -> None:
        self._animations.append(animation)

    def update(self, dt: float) -> None:
        for animation in self._animations:
            animation.update(dt)
        self._animations = [
            a for a in self._animations if not a.finished
        ]


class GameScene(Scene):
    def __init__(self,
                 state: GameState,
                 logic: GameLogic, prev_scene: Scene) -> None:
        super().__init__()
        self.logic = logic
        self.state = state
        self.anim_manager = AnimationManager()
        self.main_menu = prev_scene

    def update(self, dt: float) -> None:
        self.logic.update(self.state, dt)
        for event in self.state.events:
            if isinstance(event, GameOverEvent):
                self.switch_to(
                    FinalScene(
                        self.main_menu,
                        self.logic,
                        self.state.live_status.current_score,
                        False))
            elif isinstance(event, VictoryEvent):
                self.switch_to(
                    FinalScene(
                        self.main_menu,
                        self.logic,
                        self.state.live_status.current_score,
                        True))
        self.anim_manager.update(dt)
        self.state.events.clear

    def handle_event(self, event: InputEvent) -> None:
        if event.type == "quit":
            return
        if event.type == "keydown":
            if event.key == "up" or event.key == "w":
                self.logic.update_direction(self.state, Direction.UP)
            if event.key == "down" or event.key == "s":
                self.logic.update_direction(self.state, Direction.DOWN)
            if event.key == "left" or event.key == "a":
                self.logic.update_direction(self.state, Direction.LEFT)
            if event.key == "right" or event.key == "d":
                self.logic.update_direction(self.state, Direction.RIGHT)
            if event.key == "space":
                self.switch_to(PauseScene(self, self.main_menu))
            if event.key == "escape":
                self.switch_to(self.main_menu)

    def render(self, renderer: Renderer) -> None:
        renderer.draw(self.state)
