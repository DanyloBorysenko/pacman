from typing import List
import numpy as np
from ..state import (
    GameState, Pacman, Direction, Ghost,
    GameConfig, GameStats, GameStartEvent)
from mazegenerator.mazegenerator import MazeGenerator
from ..backend.score_board_handler import ScoreBoardHandler
from .game_initializer import GameInitializer
from .game_state_manager import GameStateManager
from .ghost_movement_logic import PseudoRandomMovement


class GameLogic:
    def __init__(self, generator: MazeGenerator, config: GameConfig):
        self.generator = generator
        self.maze = generator.maze
        self.config = config
        self.score_board = ScoreBoardHandler(config.high_score_filename)

    def create_default_state(self) -> GameState:
        state = GameState(
            maze=np.array(self.maze),
            pacman=Pacman(0, 0),
            ghosts=self._initialize_ghost(),
            live_status=GameStats(),
            config=self.config)
        GameInitializer(game_state=state).initialize()
        self.game_manager = GameStateManager(state)
        state.events.append(GameStartEvent())
        return state

    def _initialize_ghost(self) -> List[Ghost]:
        return [
            Ghost(colour="red", strategy=PseudoRandomMovement(0.95),
                  initial_colour="red"),
            Ghost(colour="pink", strategy=PseudoRandomMovement(0.3),
                  initial_colour="pink"),
            Ghost(colour="orange", strategy=PseudoRandomMovement(0.5),
                  initial_colour="orange"),
            Ghost(colour="green", strategy=PseudoRandomMovement(0.9),
                  initial_colour="green"),
        ]

    def update(self, state: GameState, dt: float) -> None:
        pacman = state.pacman
        if pacman.direction is None:
            pacman.direction = Direction.UP
            pacman.assigned_direction = Direction.UP
        pacman.mouth_phase += dt * 8
        self.game_manager.update_remaining_time(dt)
        self.game_manager.update_pacman(dt, pacman.direction)
        self.game_manager.update_ghosts(dt)
        self.game_manager.check_collisions()

    def update_direction(self, state: GameState, direction: Direction) -> None:
        # print(f"pacman direction before: {state.pacman.direction}")
        if direction is None:
            direction = Direction.UP
        state.pacman.direction = direction

    # def apply_pause(self, state: GameState) -> None:
    #     state.paused = not state.paused

    def activate_cheat_mode(self, state: GameState, key: str) -> None:
        if key == "i":
            state.cheat_invincibility = not state.cheat_invincibility
            print(f"[CHEAT] Invincibility is now: {state.cheat_invincibility}")
        if key == "l":
            print("[CHEAT] Skipping current level layout!")
            self.game_manager.level_clearance_action.advance_to_next_level(
                state)
        if key == "e":
            print("[CHEAT] Increased number of life by 1.")
            state.live_status.lives_remain += 1
        if key == "f":
            state.cheat_freeze = not state.cheat_freeze
            print(f"[CHEAT] Ghost freezing is now: {state.cheat_freeze}")
