from ..scene import Scene
from .final_scene import FinalScene
from .pause_scene import PauseScene
from src.logic import GameLogic
from src.state import Direction, GameState, GameOverEvent, VictoryEvent, PacmanDiedEvent, Pacman, Ghost, GhostEatenEvent
from ..event import InputEvent
from ..renderer import Renderer
from typing import List
from abc import ABC, abstractmethod


class Animation(ABC):
    blocking: bool = False

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @property
    @abstractmethod
    def finished(self) -> bool:
        pass

    @abstractmethod
    def on_finish(self) -> None:
        pass


class PacmanDeathAnimation(Animation):
    blocking = True

    def __init__(self, pacman: Pacman):
        self.pacman = pacman
        self.total = 1.0
        self.timer = self.total

    def update(self, dt: float) -> None:
        self.timer -= dt
        self.pacman.death_phase = 1.0 - (self.timer / self.total)

    @property
    def finished(self):
        return self.timer <= 0

    def on_finish(self) -> None:
        self.pacman.death_phase = 0.0


class GhostDeathAnimation(Animation):
    blocking = True

    def __init__(self, ghost: Ghost):
        self.ghost = ghost
        self.total = 1.0
        self.timer = self.total

    def update(self, dt: float) -> None:
        self.timer -= dt
        progress = min(1.0, 1.0 - self.timer / self.total)
        self.ghost.alpha = 1.0 - progress

    @property
    def finished(self):
        return self.timer <= 0

    def on_finish(self) -> None:
        self.ghost.alpha = 1.0


class AnimationManager:
    def __init__(self):
        self._animations: List[Animation] = []

    def add(self, animation: Animation) -> None:
        self._animations.append(animation)

    def update(self, dt: float) -> None:
        alive = []

        for animation in self._animations:
            animation.update(dt)

            if animation.finished:
                animation.on_finish()
            else:
                alive.append(animation)
        self._animations = alive

    def has_blocking(self) -> bool:
        return any([a.blocking for a in self._animations])


class GameScene(Scene):
    def __init__(self,
                 state: GameState,
                 logic: GameLogic, prev_scene: Scene) -> None:
        super().__init__()
        self.logic = logic
        self.state = state
        self.anim_manager = AnimationManager()
        self.main_menu = prev_scene
        self.counter = 0

    def update(self, dt: float) -> None:
        self.anim_manager.update(dt)
        if not self.anim_manager.has_blocking():
            self.state.pacman.mouth_phase += dt * 8
            self.logic.update(self.state, dt)
            if self.state.live_status.current_score > 20 and self.counter == 0:
                # self.state.events.append(VictoryEvent(self.state.live_status.current_score))
                # self.state.events.append(PacmanDiedEvent(self.state.pacman))
                self.state.events.append(GhostEatenEvent(self.state.ghosts[0]))
                self.counter += 1
            self._process_events()

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

    def _process_events(self) -> None:
        for event in self.state.events:
            if isinstance(event, PacmanDiedEvent):
                self.anim_manager.add(PacmanDeathAnimation(self.state.pacman))
            if isinstance(event, GhostEatenEvent):
                self.anim_manager.add(GhostDeathAnimation(event.ghost))
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
        self.state.events.clear()
