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
    """Base class for gameplay animations.

    Defines the interface for animations that update over time,
    can optionally block gameplay, and render visual effects.
    """
    blocking: bool = False

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advances the animation by dt seconds."""
        pass

    @property
    @abstractmethod
    def finished(self) -> bool:
        """Returns whether the animation has completed."""
        pass

    @abstractmethod
    def on_finish(self) -> None:
        """Performs cleanup after the animation finishes."""
        pass

    @abstractmethod
    def draw(self, renderer: Renderer) -> None:
        """Draws the animation using the given Renderer."""
        pass


class ExplosionParticle:
    """Represents a single particle in Pac-Man's death explosion."""
    __slots__ = ("dx", "dy", "vx", "vy", "size", "color")

    def __init__(self) -> None:
        """Initializes the particle with a random direction and speed."""
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.0, 3.5)  # grid cells per second
        self.dx = 0.0
        self.dy = 0.0
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.uniform(2, 5)
        self.color = "yellow"


class PacmanDeathAnimation(Animation):
    """Animates Pac-Man's death and explosion sequence."""
    blocking = True

    def __init__(self, pacman: Pacman, death_coord: Tuple[float, float],
                 ghosts: List[Ghost], on_finish: Any,
                 explosion_time: float = 1.5):
        """Initializes the death animation and explosion effect."""
        self.pacman = pacman
        self.ghosts = ghosts
        self.death_coord = death_coord
        self.direction = pacman.direction or Direction.RIGHT
        self.total = 1.0
        self.timer = self.total
        self.explosion_time = explosion_time
        self.explosion_timer = explosion_time
        self.particles: List[ExplosionParticle] = []
        self._exploded = False
        self._on_finish = on_finish

    def update(self, dt: float) -> None:
        """Advances the animation and updates explosion particles."""
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
        """Returns whether the animation has completed."""
        return self._exploded and self.explosion_timer <= 0

    def on_finish(self) -> None:
        """Restores the game state after the animation finishes."""
        self.pacman.death_phase = 0.0
        for ghost in self.ghosts:
            ghost.alpha = 1.0
        self._on_finish()

    def draw(self, renderer: Renderer) -> None:
        """Draws the death animation and explosion particles."""
        if not self._exploded:
            renderer.draw_pacman_death(
                self.death_coord[0],
                self.death_coord[1],
                self.direction, self.pacman.death_phase)
        if self.particles:
            renderer.draw_pacman_explosion(
                self.death_coord[0], self.death_coord[1], self.particles)


class GhostDeathAnimation(Animation):
    """Animates a defeated ghost and its awarded score."""
    blocking = False

    def __init__(
            self,
            ghost: Ghost,
            death_coord: Tuple[float, float],
            points_per_ghost: int) -> None:
        """Initializes the ghost death animation."""
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
        """Advances the animation and moves the score display."""
        self.timer -= dt
        progress = min(1.0, 1.0 - self.timer / self.total)
        self.ghost.alpha = 1.0 - progress
        self.score_coord_y = self.score_coord_y - dt * self.scores_speed

    @property
    def finished(self) -> bool:
        """Returns whether the animation has completed."""
        return self.timer <= 0

    def on_finish(self) -> None:
        """Restores the ghost's visual state."""
        self.ghost.alpha = 1.0

    def draw(self, renderer: Renderer) -> None:
        """Draws the ghost and its score bonus."""
        renderer.draw_ghost(self.ghost)
        renderer.draw_scores(
            f"+{self.points_per_ghost}",
            self.score_coord_x, self.score_coord_y)


class GameOverAnimation(Animation):
    """Displays the animated Game Over screen."""
    blocking = True

    def __init__(self, on_finish: Any, grow_time: float = 0.8,
                 hold_time: float = 1.5) -> None:
        """Initializes the Game Over animation."""
        self.grow_time = grow_time
        self.hold_time = hold_time
        self.total = grow_time + hold_time
        self.elapsed = 0.0
        self.scale = 0.0
        self.alpha = 0
        self._on_finish = on_finish

    def update(self, dt: float) -> None:
        """Advances the animation."""
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.grow_time)
        self.scale = progress
        self.alpha = int(180 * progress)

    @property
    def finished(self) -> bool:
        """Returns whether the animation has completed."""
        return self.elapsed >= self.total

    def on_finish(self) -> None:
        """Performs the configured action after the animation ends."""
        self._on_finish()

    def draw(self, renderer: Renderer) -> None:
        """Draws the Game Over animation."""
        renderer.apply_blur()
        renderer.draw_game_over_text(self.scale, self.alpha)


class ConfettiParticle:
    """Represents a single confetti particle used in the victory animation."""
    __slots__ = ("x", "y", "vx", "vy", "size",
                 "color", "rotation", "rot_speed")

    def __init__(self, x: float, y: float) -> None:
        """Initializes the particle with random motion and appearance."""
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
    """Displays the victory animation with confetti effects."""
    blocking = True

    GRAVITY = 500

    def __init__(self,
                 on_finish: Any, grow_time: float = 0.6,
                 hold_time: float = 2.5,
                 particle_count: int = 120) -> None:
        """Initializes the victory animation."""
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
        """Advances the animation and updates the confetti particles."""
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
        """Returns whether the animation has completed."""
        return self.elapsed >= self.total

    def on_finish(self) -> None:
        """Performs the configured action after the animation ends."""
        self._on_finish()

    def draw(self, renderer: Renderer) -> None:
        """Draws the victory animation."""
        renderer.draw_confetti(self.particles)
        renderer.draw_victory_text(self.scale, self.alpha)


class GameStartAnimation(Animation):
    """Displays the countdown before gameplay begins."""
    blocking = True

    def __init__(self, grow_time: float = 0.6, hold_time: float = 0.4,
                 texts: tuple[str, ...] = ("3", "2", "1")):
        """Initializes the countdown animation."""
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
        """Advances the countdown animation."""
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
        """Returns whether the countdown has completed."""
        return self.elapsed >= self.total

    def on_finish(self) -> None:
        """Performs cleanup after the countdown finishes."""
        pass

    def draw(self, renderer: Renderer) -> None:
        """Draws the current countdown value."""
        renderer.draw_start(self.scale, self.current_text)


class LevelUpAnimation(Animation):
    """Displays the level transition animation."""
    blocking = True

    def __init__(self, current_level: int, on_finish: Callable,
                 grow_time: float = 0.6, hold_time: float = 1.2):
        """Initializes the level-up animation."""
        self.grow_time = grow_time
        self.hold_time = hold_time
        self.total = grow_time + hold_time
        self.elapsed = 0.0
        self.scale = 0.0
        self.alpha = 0
        self.level_text = f"LEVEL {current_level}"
        self._on_finish = on_finish

    def update(self, dt: float) -> None:
        """Advances the level-up animation."""
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.grow_time)
        self.scale = progress
        self.alpha = int(150 * progress)  # overlay alpha values

    @property
    def finished(self) -> bool:
        """Returns whether the animation has completed."""
        return self.elapsed >= self.total

    def on_finish(self) -> None:
        """Performs the configured action after the animation ends."""
        self._on_finish()

    def draw(self, renderer: Renderer) -> None:
        """Draws the level-up animation."""
        renderer.apply_blur()
        renderer.draw_level_up_text(self.scale, self.level_text, self.alpha)


class AnimationManager:
    """Manages all active gameplay animations."""
    def __init__(self) -> None:
        """Initializes an empty animation manager."""
        self._animations: List[Animation] = []

    def add(self, animation: Animation) -> None:
        """Adds an animation to the active animation list."""
        self._animations.append(animation)

    def update(self, dt: float) -> None:
        """Updates all active animations and removes completed ones."""
        alive = []

        for animation in self._animations:
            animation.update(dt)

            if animation.finished:
                animation.on_finish()
            else:
                alive.append(animation)
        self._animations = alive

    def has_blocking(self) -> bool:
        """Returns whether any active animation blocks gameplay."""
        return any([a.blocking for a in self._animations])

    def draw(self, render: Renderer) -> None:
        """Draws all active animations."""
        for animation in self._animations:
            animation.draw(render)


class GameScene(Scene):
    """Primary gameplay scene.

    Runs the game loop, processes player input, updates the game
    state, manages animations and audio, and renders the current
    game world. It also handles game events and transitions to
    pause, final, or main menu scenes when appropriate.
    """
    def __init__(self,
                 state: GameState,
                 logic: GameLogic, prev_scene: Scene) -> None:
        """Initializes the gameplay scene with the current game
        state, game logic, animations, and audio resources."""
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
        self.sound_fruit_eating = pygame.mixer.Sound(
            GameAudioFile.FRUIT_EATING.value)

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
        """Advances the game by dt seconds.

        Processes game events, updates animations, manages audio
        playback, and updates the game state while no blocking
        animation is active.
        """
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

        if not self.anim_manager.has_blocking():
            self.state.pacman.mouth_phase += dt * 8
            self.logic.update(self.state, dt)
            self._process_events()

    def start_audio(self) -> None:
        """Executed automatically via Controller hook when
        entering gameplay."""
        if self.intro_playing:
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
        """Handles player input.

        Updates Pac-Man's movement direction, pauses or exits the
        game, and processes cheat-mode key presses.
        """
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
                self.switch_to(PauseScene(
                    self, self.main_menu,
                    self.sound_ghost_chasing))
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
        elif event.type in [pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN]:
            # Convert normalized finger position to actual pixels if needed
            if hasattr(event, "x") and hasattr(event, "y"):
                touch_pos = (event.x * WINDOW_WIDTH, event.y * WINDOW_HEIGHT)

            # 1. Map D-Pad Directions to the Physics Engine
            if self.touch_up.collidepoint(touch_pos):
                self.logic.update_direction(self.state, Direction.UP)
            elif self.touch_down.collidepoint(touch_pos):
                self.logic.update_direction(self.state, Direction.DOWN)
            elif self.touch_left.collidepoint(touch_pos):
                self.logic.update_direction(self.state, Direction.LEFT)
            elif self.touch_right.collidepoint(touch_pos):
                self.logic.update_direction(self.state, Direction.RIGHT)

            # Action Button Routing
            elif self.touch_enter.collidepoint(touch_pos):
                self.switch_to(PauseScene(self, self.main_menu))
            # Back Button Routing (Clean Exit to Main Menu)
            elif self.touch_back.collidepoint(touch_pos):
                self.stop_audio()
                self.switch_to(self.main_menu)

    def render(self, renderer: Renderer) -> None:
        """Draws the current game state and all active animations."""
        renderer.draw(self.state)
        self.draw_mobile_controls(renderer.surface)
        self.anim_manager.draw(renderer)

    def _process_events(self) -> None:
        """Processes queued game events.

        Plays sounds, starts animations, and performs scene
        transitions in response to gameplay events such as deaths,
        level completion, victory, or game over."""
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
