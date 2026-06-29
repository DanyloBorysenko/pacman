from src.state import (GameState, Pacman, Direction,
                       Ghost, GameConfig, GameStats)
from mazegenerator.mazegenerator import MazeGenerator
from .backend.game_initializer import GameInitializer
from .backend.game_state_manager import GameStateManager


class GameLogic:
    def __init__(self, generator: MazeGenerator):
        self.generator = generator
        self.maze = generator.maze

    def create_default_state(self) -> GameState:
        state = GameState(
            maze=self.maze,
            pacman=Pacman(0, 0, None),
            ghosts=[
                Ghost(0, 0, Direction.LEFT, False, None, "red"),
                Ghost(0, 0, Direction.RIGHT, False, None, "red"),
                Ghost(0, 0, Direction.UP, False, None, "red"),
                Ghost(0, 0, Direction.DOWN, False, None, "red")],
            live_status=GameStats(),
            config=GameConfig)
        GameInitializer(game_state=state).initialize()
        self.game_manager = GameStateManager(state)
        return state

    def update(self, state: GameState, dt: float) -> None:
        pacman = state.pacman
        pacman.mouth_phase += dt * 8
        self.game_manager.update(dt, pacman.direction)

    def update_direction(self, state: GameState, direction: Direction) -> None:
        state.pacman.direction = direction

    def apply_pause(self, state: GameState) -> None:
        state.paused = not state.paused
