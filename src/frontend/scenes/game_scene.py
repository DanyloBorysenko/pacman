from dataclasses import replace
import random
import math
import pygame
from typing import Callable, Any
from ..scene import Scene
from ...backend.logic import GameLogic
from .final_scene import FinalScene
from .pause_scene import PauseScene
from ...state import (
    Direction, GameState, GameOverEvent, VictoryEvent,
    PacmanDiedEvent, Pacman, Ghost, GhostEatenEvent,
    GameAudioFile, GameStartEvent, GumEatenEvent,
    LevelUpEvent, CherryEatenEvent)
from ..event import InputEvent
from ..renderer import Renderer
from typing import List, Tuple
from abc import ABC, abstractmethod
from ...constants import WINDOW_WIDTH, WINDOW_HEIGHT


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
                 ghosts: List[Ghost], on_finish: Any,
                 explosion_time: float = 1.5):
        self.pacman = pacman
        self.ghosts = ghosts
        self.death_coord = death_coord
        self.total = 1.0
        self.timer = self.total
        self.explosion_time = explosion_time
        self.explosion_timer = explosion_time
        self.particles: List[ExplosionParticle] = []
        self._exploded = False
        self._on_finish = on_finish

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
    def finished(self) -> bool:
        return self._exploded and self.explosion_timer <= 0

    def on_finish(self) -> None:
        self.pacman.death_phase = 0.0
        for ghost in self.ghosts:
            ghost.alpha = 1.0
        self._on_finish()

    def draw(self, renderer: Renderer) -> None:
        if not self._exploded:
            renderer.draw_pacman_death(
                self.death_coord[0],
                self.death_coord[1], self.pacman.death_phase)
        if self.particles:
            renderer.draw_pacman_explosion(
                self.death_coord[0], self.death_coord[1], self.particles)


class GhostDeathAnimation(Animation):
    blocking = False

    def __init__(
            self,
            ghost: Ghost,
            death_coord: Tuple[float, float],
            points_per_ghost: int) -> None:
        self.ghost = replace(ghost)
        self.death_coord = death_coord
        self.ghost.x = self.death_coord[0]
        self.ghost.y = self.death_coord[1]
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
    def finished(self) -> bool:
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

    def __init__(self, on_finish: Any, grow_time: float = 0.8,
                 hold_time: float = 1.5) -> None:
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
    __slots__ = ("x", "y", "vx", "vy", "size",
                 "color", "rotation", "rot_speed")

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

    def __init__(self,
                 on_finish: Any, grow_time: float = 0.6,
                 hold_time: float = 2.5,
                 particle_count: int = 120) -> None:
        self.grow_time = grow_time
        self.hold_time = hold_time
        self.total = grow_time + hold_time
        self.elapsed = 0.0
        self.scale = 0.0
        self.alpha = 0
        self._on_finish = on_finish

        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        self.particles = [ConfettiParticle(cx, cy) for _ in range(
            particle_count)]

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

        index = min(int(
            self.elapsed // self.segment_time), len(self.texts) - 1)
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


class LevelUpAnimation(Animation):
    blocking = True

    def __init__(self, current_level: int, on_finish: Callable,
                 grow_time: float = 0.6, hold_time: float = 1.2):
        self.grow_time = grow_time
        self.hold_time = hold_time
        self.total = grow_time + hold_time
        self.elapsed = 0.0
        self.scale = 0.0
        self.alpha = 0
        self.level_text = f"LEVEL {current_level}"
        self._on_finish = on_finish

    def update(self, dt: float) -> None:
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.grow_time)
        self.scale = progress
        self.alpha = int(150 * progress)  # overlay alpha values

    @property
    def finished(self) -> bool:
        return self.elapsed >= self.total

    def on_finish(self) -> None:
        self._on_finish()

    def draw(self, renderer: Renderer) -> None:
        renderer.apply_blur()
        renderer.draw_level_up_text(self.scale, self.level_text, self.alpha)


class AnimationManager:
    def __init__(self) -> None:
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

        # Game Audio file
        self.sound_intro = pygame.mixer.Sound(GameAudioFile.INTRO.value)
        self.sound_pacman_munch = pygame.mixer.Sound(
            GameAudioFile.PACMAN_MUNCH.value)
        self.sound_ghost_eating = pygame.mixer.Sound(
            GameAudioFile.GHOST_EATING.value)
        self.sound_ghost_chasing = pygame.mixer.Sound(
            GameAudioFile.GHOST_CHASING.value)
        self.sound_ghost_fleeing = pygame.mixer.Sound(
            GameAudioFile.GHOST_FLEEING.value)
        self.sound_death = pygame.mixer.Sound(GameAudioFile.DEATH.value)
        self.sound_fruit_eating = pygame.mixer.Sound(GameAudioFile.FRUIT_EATING.value)

        # Game Audio Volume
        self.sound_intro.set_volume(0.3)
        self.sound_pacman_munch.set_volume(0.5)
        self.sound_ghost_eating.set_volume(0.7)
        self.sound_ghost_chasing.set_volume(0.2)
        self.sound_fruit_eating.set_volume(0.6)
        self.sound_death.set_volume(0.6)

        self.siren_playing = False
        self.intro_playing = True

    def update(self, dt: float) -> None:
        self._process_events()
        self.anim_manager.update(dt)

        if self.intro_playing:
            if not self.anim_manager.has_blocking():
                self.intro_playing = False
                self.sound_ghost_chasing.play(loops=-1)

        if not self.intro_playing:
            any_ghost_edible = any(g.is_edible for g in self.state.ghosts)
            if any_ghost_edible and not self.siren_playing:
                self.sound_ghost_chasing.stop()
                self.sound_ghost_fleeing.play(loops=-1)
                self.siren_playing = True
            elif not any_ghost_edible and self.siren_playing:
                self.sound_ghost_fleeing.stop()
                self.sound_ghost_chasing.play(loops=-1)
                self.siren_playing = False
            # elif not any_ghost_edible and not self.siren_playing:
            #     self.sound_ghost_chasing.play(loops=-1)
            #     self.siren_playing = True

        if not self.anim_manager.has_blocking():
            self.state.pacman.mouth_phase += dt * 8
            self.logic.update(self.state, dt)
            # if self.state.live_status.current_score > 20 and\
            #     self.counter == 0:
            #     # self.state.events.append(
            # GameOverEvent(self.state.live_status.current_score))
            #     # self.state.events.append(
            # VictoryEvent(self.state.live_status.current_score))
            #     self.state.events.append(
            # PacmanDiedEvent(self.state.pacman))
            #     # self.state.events.append(
            # GhostEatenEvent(self.state.ghosts.pop(0)))
            #     self.counter += 1
            self._process_events()

    def start_audio(self) -> None:
        """Executed automatically via Controller hook when
        entering gameplay."""
        self.sound_intro.play()
        # self.sound_ghost_chasing.play(loops=-1)

    def stop_audio(self) -> None:
        """Executed automatically via Controller hook when
        exiting to main menu."""
        self.sound_intro.stop()
        self.sound_ghost_chasing.stop()
        self.sound_ghost_fleeing.stop()
        self.siren_playing = False

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
                self.logic.activate_cheat_mode(self.state, event.key)
            if event.key == "l":
                self.logic.activate_cheat_mode(self.state, event.key)
            if event.key == "e":
                self.logic.activate_cheat_mode(self.state, event.key)
            if event.key == "f":
                self.logic.activate_cheat_mode(self.state, event.key)

    def render(self, renderer: Renderer) -> None:
        renderer.draw(self.state)
        self.anim_manager.draw(renderer)

    def _process_events(self) -> None:
        for event in self.state.events:
            if isinstance(event, GumEatenEvent):
                self.sound_pacman_munch.play()
            if isinstance(event, GameStartEvent):
                self.anim_manager.add(GameStartAnimation())
                self.sound_intro.play()
            if isinstance(event, PacmanDiedEvent):
                self.stop_audio()
                self.sound_death.play()
                self.anim_manager.add(
                    PacmanDeathAnimation(
                        pacman=self.state.pacman,
                        death_coord=event.death_coord,
                        ghosts=self.state.ghosts,
                        on_finish=lambda: self.sound_ghost_chasing.play(
                            loops=-1)
                        )
                    )
            if isinstance(event, GhostEatenEvent):
                points_per_ghost = (100 if not self.state.config
                                    else self.state.config.points_per_ghost)
                self.anim_manager.add(GhostDeathAnimation(
                    event.ghost, event.death_coord, points_per_ghost))
                self.sound_ghost_eating.play()
            if isinstance(event, LevelUpEvent):
                self.stop_audio()
                level_num = event.next_level
                self.anim_manager.add(
                    LevelUpAnimation(
                        current_level=level_num,
                        on_finish=lambda: self.sound_ghost_chasing.play(
                            loops=-1)
                    )
                )
            if isinstance(event, CherryEatenEvent):
                self.sound_fruit_eating.play()
            if isinstance(event, GameOverEvent):
                self.stop_audio()
                # self.sound_death.play()
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
