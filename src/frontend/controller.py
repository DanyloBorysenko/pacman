from .renderer import Renderer
from ..backend.logic import GameLogic
from ..constants import WINDOW_WIDTH, WINDOW_HEIGHT
from .scenes.main_menu_scene import MainMenuScene
from .scenes.final_scene import FinalScene
from .scene import Scene
from .event import InputEvent
from ..state import GameAudioFile
import pygame
import pygame_textinput
from typing import Any


class Controller:
    """Owns the pygame main loop: initializes the window, renderer
    and audio, translates raw pygame events into InputEvents, and
    drives the active Scene's handle_event/update/render cycle,
    swapping scenes as they request via Scene.next_scene."""

    def __init__(self, logic: GameLogic):
        """Sets up pygame, the display window, renderer, key
        mapping, text input, and background audio, and starts on
        the MainMenuScene."""
        pygame.init()
        self.events_keys_dict = {
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
            pygame.K_SPACE: "space",
            pygame.K_RETURN: "enter",
            pygame.K_ESCAPE: "escape",
            pygame.K_w: "w",
            pygame.K_s: "s",
            pygame.K_a: "a",
            pygame.K_d: "d",
            pygame.K_i: "i",       # Added for Invincibility cheat toggle
            pygame.K_l: "l",       # Added for Skip Level cheat trigger
            pygame.K_e: "e",       # Added for extra life
            pygame.K_f: "f"        # Added for ghost freeze
        }
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.Clock()
        self.renderer = Renderer(self.screen)
        self.current_scene: Scene = MainMenuScene(logic)
        self.text_input = pygame_textinput.TextInputManager(
            validator=lambda name: len(name) <= 10)

        self.background_sound = pygame.mixer.Sound(
            GameAudioFile.BACKGROUND.value)
        self.background_sound.set_volume(0.2)

    def set_running_status(self, status: bool) -> None:
        self.running = status

    def start_background_music(self) -> None:
        self.background_sound.play(loops=-1)

    def run_single_scene(self) -> None:
        raw_events = pygame.event.get()
        wants_text = getattr(self.current_scene, "wants_text_input", False)
        if wants_text:
            self.text_input.update(raw_events)
        dt = self.clock.tick(60) / 1000
        for event in raw_events:
            self._check_touch(event)
            if self._should_exit(event):
                self.running = False
            inp_event = self._to_input_event(event)
            if inp_event is not None:
                self.current_scene.handle_event(inp_event)
        if wants_text:
            if isinstance(self.current_scene, FinalScene):
                self.current_scene.set_text_input(self.text_input.value)
        self.current_scene.update(dt)
        next_scene = self.current_scene.next_scene
        if next_scene:
            if hasattr(self.current_scene, "stop_audio"):
                self.current_scene.stop_audio()
                self.background_sound.play(loops=-1)
            self.text_input.value = ""

            self.current_scene = next_scene

            if hasattr(self.current_scene, "start_audio"):
                self.background_sound.stop()
                self.current_scene.start_audio()

        self.screen.fill("black")
        self.current_scene.render(self.renderer)
        pygame.display.update()

    def _check_touch(self, event: Any) -> None:
        if event.type in [pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN]:
            if hasattr(event, "x") and hasattr(event, "y"):
                touch_pos = (event.x * WINDOW_WIDTH, event.y * WINDOW_HEIGHT)
            else:
                touch_pos = event.pos

            active = self.current_scene
            virtual_key = None

            if not hasattr(active, "touch_up"):
                return

            # Translate screen touches directly to standard keyboard signals
            if active.touch_up.collidepoint(touch_pos):
                virtual_key = pygame.K_UP
            elif active.touch_down.collidepoint(touch_pos):
                virtual_key = pygame.K_DOWN
            elif active.touch_left.collidepoint(touch_pos):
                virtual_key = pygame.K_LEFT
            elif active.touch_right.collidepoint(touch_pos):
                virtual_key = pygame.K_RIGHT
            elif active.touch_enter.collidepoint(touch_pos):
                virtual_key = pygame.K_RETURN  # Maps to Enter
            elif active.touch_back.collidepoint(touch_pos):
                virtual_key = pygame.K_ESCAPE  # Maps to Escape

            if virtual_key is not None:
                # Create a fake Pygame KEYDOWN event
                fake_event = pygame.event.Event(
                    pygame.KEYDOWN, key=virtual_key)
                pygame.event.post(fake_event)

    def run(self) -> None:
        """Runs the main game loop until exit: polls events, feeds
        them to the active scene, updates/renders it each frame,
        and swaps to the next scene (including audio handoff) when
        one is queued."""
        self.set_running_status(True)
        self.start_background_music()
        while self.running:
            self.run_single_scene()
        pygame.quit()

    def _to_input_event(self,
                        pygame_event: pygame.event.Event) -> InputEvent | None:
        """Converts a raw pygame event into an InputEvent, or None
        if the event type isn't one the game reacts to."""
        input_event = None
        if pygame_event.type == pygame.QUIT:
            input_event = InputEvent(type="quit", key=None)
        elif pygame_event.type == pygame.KEYDOWN:
            key = self.events_keys_dict.get(pygame_event.key, None)
            input_event = InputEvent(type="keydown", key=key)
        return input_event

    def _should_exit(self, event: pygame.event.Event) -> bool:
        """Returns True if the game window should close: on a QUIT
        event, or Escape pressed while on the main menu."""
        if (event.type == pygame.QUIT):
            return True
        if (event.type == pygame.KEYDOWN
           and event.key == pygame.K_ESCAPE
           and isinstance(self.current_scene, MainMenuScene)):
            return True
        return False
