from ..scene import Scene
from src.backend.logic import GameLogic
from .final_scene import FinalScene
from .pause_scene import PauseScene
from src.state import (Direction, GameState, GameOverEvent, VictoryEvent,
                       PacmanDiedEvent, Pacman, Ghost, GhostEatenEvent,
                       GameConfig, GameStartEvent)
from ..event import InputEvent
from ..renderer import Renderer
from typing import List, Tuple
from abc import ABC, abstractmethod
from ...constants import WINDOW_WIDTH, WINDOW_HEIGHT
import random
import math


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

    @abstractmethod
    def draw(self, renderer: Renderer) -> None:
        pass


class ExplosionParticle:
    __slots__ = ("dx", "dy", "vx", "vy", "size", "color")

    def __init__(self) -> None:
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.0, 3.5)  # grid cells per second
        self.dx = 0.0
        self.dy = 0.0
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.uniform(2, 5)
        self.color = "yellow"


class PacmanDeathAnimation(Animation):
    blocking = True

    def __init__(self, pacman: Pacman, death_coord: Tuple[float, float],
                 ghosts: List[Ghost], explosion_time: float = 1.5):
        self.pacman = pacman
        self.ghosts = ghosts
        self.death_coord = death_coord
        self.total = 1.0
        self.timer = self.total
        self.explosion_time = explosion_time
        self.explosion_timer = explosion_time
        self.particles: List[ExplosionParticle] = []
        self._exploded = False

    def update(self, dt: float) -> None:
        for ghost in self.ghosts:
            ghost.alpha = 0.0
        if self.timer > 0:
            self.timer -= dt
            self.pacman.death_phase = 1.0 - (self.timer / self.total)

        if self.pacman.death_phase >= 0.999 and not self._exploded:
            self._exploded = True
            self.particles = [ExplosionParticle() for _ in range(24)]

        if self._exploded:
            self.explosion_timer -= dt
            for p in self.particles:
                p.dx += p.vx * dt
                p.dy += p.vy * dt
                p.vx *= 0.9
                p.vy *= 0.9

    @property
    def finished(self):
        return self._exploded and self.explosion_timer <= 0

    def on_finish(self) -> None:
        self.pacman.death_phase = 0.0
        for ghost in self.ghosts:
            ghost.alpha = 1.0

    def draw(self, renderer: Renderer) -> None:
        if not self._exploded:
            renderer.draw_pacman_death(
                self.death_coord[0],
                self.death_coord[1], self.pacman.death_phase)
        if self.particles:
            renderer.draw_pacman_explosion(
                self.death_coord[0], self.death_coord[1], self.particles)


class GhostDeathAnimation(Animation):
    blocking = True

    def __init__(
            self,
            ghost: Ghost,
            death_coord: Tuple[float, float],
            points_per_ghost: int) -> None:
        self.ghost = ghost
        self.points_per_ghost = points_per_ghost
        self.total = 1.0
        self.timer = self.total
        self.score_coord_x = death_coord[0]
        self.score_coord_y = death_coord[1]
        self.scores_speed = 1.0

    def update(self, dt: float) -> None:
        self.timer -= dt
        progress = min(1.0, 1.0 - self.timer / self.total)
        self.ghost.alpha = 1.0 - progress
        self.score_coord_y = self.score_coord_y - dt * self.scores_speed

    @property
    def finished(self):
        return self.timer <= 0

    def on_finish(self) -> None:
        self.ghost.alpha = 1.0

    def draw(self, renderer: Renderer) -> None:
        renderer.draw_ghost(self.ghost)
        renderer.draw_scores(
            f"+{self.points_per_ghost}",
            self.score_coord_x, self.score_coord_y)


class GameOverAnimation(Animation):
    blocking = True

    def __init__(self, on_finish, grow_time: float = 0.8, hold_time: float = 1.5):
        self.grow_time = grow_time
        self.hold_time = hold_time
        self.total = grow_time + hold_time
        self.elapsed = 0.0
        self.scale = 0.0
        self.alpha = 0
        self._on_finish = on_finish

    def update(self, dt: float) -> None:
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.grow_time)
        self.scale = progress
        self.alpha = int(180 * progress)

    @property
    def finished(self) -> bool:
        return self.elapsed >= self.total

    def on_finish(self) -> None:
        self._on_finish()

    def draw(self, renderer: Renderer) -> None:
        renderer.apply_blur()
        renderer.draw_game_over_text(self.scale, self.alpha)


class ConfettiParticle:
    __slots__ = ("x", "y", "vx", "vy", "size", "color", "rotation", "rot_speed")

    def __init__(self, x: float, y: float) -> None:
        angle = random.uniform(0, math.tau)
        speed = random.uniform(150, 400)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 200  # bias upward for the "pop"
        self.size = random.uniform(4, 9)
        self.color = random.choice([
            "red", "yellow", "cyan", "magenta", "lime", "orange", "white"
        ])
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-360, 360)


class VictoryAnimation(Animation):
    blocking = True

    GRAVITY = 500

    def __init__(self, on_finish, grow_time: float = 0.6, hold_time: float = 2.5,
                 particle_count: int = 120):
        self.grow_time = grow_time
        self.hold_time = hold_time
        self.total = grow_time + hold_time
        self.elapsed = 0.0
        self.scale = 0.0
        self.alpha = 0
        self._on_finish = on_finish

        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        self.particles = [ConfettiParticle(cx, cy) for _ in range(particle_count)]

    def update(self, dt: float) -> None:
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.grow_time)
        self.scale = progress
        self.alpha = int(120 * progress)

        for p in self.particles:
            p.vy += self.GRAVITY * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.rotation += p.rot_speed * dt

    @property
    def finished(self) -> bool:
        return self.elapsed >= self.total

    def on_finish(self) -> None:
        self._on_finish()

    def draw(self, renderer: Renderer) -> None:
        renderer.draw_confetti(self.particles)
        renderer.draw_victory_text(self.scale, self.alpha)


class GameStartAnimation(Animation):
    blocking = True

    def __init__(self, grow_time: float = 0.6, hold_time: float = 0.4,
                 texts: tuple[str, ...] = ("3", "2", "1")):
        self.texts = texts
        self.grow_time = grow_time
        self.hold_time = hold_time
        self.segment_time = grow_time + hold_time
        self.total = self.segment_time * len(texts)
        self.elapsed = 0.0
        self.scale = 0.0
        self.alpha = 0
        self.current_text = texts[0]

    def update(self, dt: float) -> None:
        self.elapsed += dt

        index = min(int(self.elapsed // self.segment_time), len(self.texts) - 1)
        self.current_text = self.texts[index]

        segment_elapsed = self.elapsed - index * self.segment_time
        progress = min(1.0, segment_elapsed / self.grow_time)
        self.scale = progress
        self.alpha = int(180 * progress)

    @property
    def finished(self) -> bool:
        return self.elapsed >= self.total

    def on_finish(self) -> None:
        pass

    def draw(self, renderer: Renderer) -> None:
        renderer.draw_start(self.scale, self.current_text)


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

    def draw(self, render: Renderer) -> None:
        for animation in self._animations:
            animation.draw(render)


class GameScene(Scene):
    def __init__(self,
                 state: GameState,
                 logic: GameLogic, prev_scene: Scene) -> None:
        super().__init__()
        self.logic = logic
        self.state = state
        self.anim_manager = AnimationManager()
        self.main_menu = prev_scene
        # self.counter = 0

    def update(self, dt: float) -> None:
        self.anim_manager.update(dt)
        if not self.anim_manager.has_blocking():
            self.state.pacman.mouth_phase += dt * 8
            self.logic.update(self.state, dt)
            # if self.state.live_status.current_score > 20 and self.counter == 0:
            #     # self.state.events.append(GameOverEvent(self.state.live_status.current_score))
            #     # self.state.events.append(VictoryEvent(self.state.live_status.current_score))
            #     self.state.events.append(PacmanDiedEvent(self.state.pacman))
            #     # self.state.events.append(GhostEatenEvent(self.state.ghosts.pop(0)))
                # self.counter += 1
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

            # --- CHEAT MODE KEY ROUTING ---
            if event.key == "i":
                self.logic.toggle_invincibility(self.state)
            if event.key == "l":
                self.logic.cheat_skip_level(self.state)

    def render(self, renderer: Renderer) -> None:
        renderer.draw(self.state)
        self.anim_manager.draw(renderer)

    def _process_events(self) -> None:
        for event in self.state.events:
            if isinstance(event, GameStartEvent):
                self.anim_manager.add(GameStartAnimation())
            if isinstance(event, PacmanDiedEvent):
                self.anim_manager.add(
                    PacmanDeathAnimation(
                        self.state.pacman,
                        event.death_coord,
                        self.state.ghosts))
            if isinstance(event, GhostEatenEvent):
                points_per_ghost = (100 if not self.state.config
                                    else self.state.config.points_per_ghost)
                self.anim_manager.add(GhostDeathAnimation(
                    event.ghost, event.death_coord, points_per_ghost))
            if isinstance(event, GameOverEvent):
                score = event.final_score
                self.anim_manager.add(GameOverAnimation(
                    lambda score=score: self.switch_to(
                        FinalScene(self.main_menu, self.logic, score, False))))
            elif isinstance(event, VictoryEvent):
                score = event.final_score
                self.anim_manager.add(VictoryAnimation(
                    lambda score=score: self.switch_to(
                        FinalScene(self.main_menu, self.logic, score, True))))
        self.state.events.clear()
