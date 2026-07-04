from src.state import (
    GameState, Pacman, Direction, Ghost,
    GameConfig, GameStats)
from mazegenerator.mazegenerator import MazeGenerator
from src.constants import CELL_SIZE
from .game_initializer import GameInitializer
from .game_state_manager import GameStateManager
from .ghost_movement import (
    RandomMovement, DirectionalMovement,
    PseudoRandomMovement
)

PACMAN_SPEED = 1

GHOSTS = [
    Ghost(colour="red", strategy=DirectionalMovement(), initial_colour="red"),
    Ghost(colour="pink", strategy=PseudoRandomMovement(), initial_colour="pink"),
    Ghost(colour="orange", strategy=PseudoRandomMovement(0.9), initial_colour="orange"),
    Ghost(colour="green", strategy=RandomMovement(), initial_colour="green"),
]


class GameLogic:
    def __init__(self, generator: MazeGenerator, config: GameConfig):
        self.generator = generator
        self.maze = generator.maze
        self.config = config

    def create_default_state(self) -> GameState:
        state = GameState(
            maze=self.maze,
            pacman=Pacman(0, 0, None),
            ghosts=GHOSTS,
            live_status=GameStats,
            config=self.config)
        GameInitializer(game_state=state).initialize()
        self.game_manager = GameStateManager(state)
        # print(state.pacman.x, state.pacman.y)
        # print(self.maze)
        return state

    def update(self, state: GameState, dt: float) -> None:
        pacman = state.pacman
        pacman.mouth_phase += dt * 8
        self.game_manager.update_remaining_time(dt)
        self.game_manager.update_pacman(dt, pacman.direction)
        self.game_manager.update_ghosts(dt)
        self.game_manager.check_collisions()

    def update_direction(self, state: GameState, direction: Direction) -> None:
        state.pacman.direction = direction

    def apply_pause(self, state: GameState) -> None:
        state.paused = not state.paused

    def toggle_invincibility(self, state: GameState) -> None:
        """Swaps player invincibility status flag on the fly."""
        state.cheat_invincibility = not state.cheat_invincibility
        print(f"[CHEAT] Invincibility is now: {state.cheat_invincibility}")

    def cheat_skip_level(self, state: GameState) -> None:
        """Instantly forces a level transition bypass."""
        print("[CHEAT] Skipping current level layout!")
        self.game_manager._advance_to_next_level()

    def _entity_cell(self, x: float, y: float) -> tuple[int, int]:
        return (
            int(y // CELL_SIZE),
            int(x // CELL_SIZE),
        )
