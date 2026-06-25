from src.state import (
    GameState, Pacman, Direction, Ghost,
    GameConfig, GameStats)
from mazegenerator.mazegenerator import MazeGenerator
from src.constants import CELL_SIZE
from .backend.game_initializer import GameInitializer
from .backend.game_state_manager import GameStateManager
from .backend.ghost_movement import (
    RandomMovement, DirectionalMovement,
    PseudoRandomMovement
)

PACMAN_SPEED = 1

GHOSTS = [
    Ghost(colour="red", strategy=DirectionalMovement()),
    Ghost(colour="blue", strategy=PseudoRandomMovement()),
    Ghost(colour="yellow", strategy=PseudoRandomMovement(0.9)),
    Ghost(colour="green", strategy=RandomMovement()),
]


class GameLogic:
    def __init__(self, generator: MazeGenerator):
        self.generator = generator
        self.maze = generator.maze

    def create_default_state(self) -> GameState:
        state = GameState(
            maze=self.maze,
            pacman=Pacman(0, 0, None),
            ghosts=GHOSTS,
            live_status=GameStats,
            config=GameConfig)
        GameInitializer(game_state=state).initialize()
        self.game_manager = GameStateManager(state)
        # print(state.pacman.x, state.pacman.y)
        return state

    def update(self, state: GameState, dt: float) -> None:
        if state.paused:
            return
        pacman = state.pacman
        pacman.mouth_phase += dt * 8
        self.game_manager.update_pacman(dt, pacman.direction)
        self.game_manager.update_ghosts(dt)
        self.game_manager.check_collisions()

    def update_direction(self, state: GameState, direction: Direction) -> None:
        state.pacman.direction = direction

    def apply_pause(self, state: GameState) -> None:
        state.paused = not state.paused

    def _entity_cell(self, x: float, y: float) -> tuple[int, int]:
        return (
            int(y // CELL_SIZE),
            int(x // CELL_SIZE),
        )
