from src.state import GameState, Pacman, Direction, Ghost, GameConfig
from mazegenerator.mazegenerator import MazeGenerator
from src.constants import CELL_SIZE
from .backend.game_initializer import GameInitializer
from .backend.game_state_manager import GameStateManager

PACMAN_SPEED = 1.0


class GameLogic:
    def __init__(self, generator: MazeGenerator):
        self.generator = generator
        self.maze = generator.maze

    def create_default_state(self) -> GameState:
        state = GameState(
            maze=self.maze,
            pacman=Pacman(0, 0, None),
            ghosts=[Ghost(0, 0, None, "red") for _ in range(4)],
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
        # self.game_manager.request_move(pacman.direction.value)
        if pacman.direction is Direction.RIGHT:
            pacman.x += PACMAN_SPEED * dt

        elif pacman.direction is Direction.LEFT:
            pacman.x -= PACMAN_SPEED * dt

        elif pacman.direction is Direction.UP:
            pacman.y -= PACMAN_SPEED * dt

        elif pacman.direction is Direction.DOWN:
            pacman.y += PACMAN_SPEED * dt

    def update_direction(self, state: GameState, direction: Direction) -> None:
        state.pacman.direction = direction

    def apply_pause(self, state: GameState) -> None:
        state.paused = not state.paused

    def _entity_cell(self, x: float, y: float) -> tuple[int, int]:
        return (
            int(y // CELL_SIZE),
            int(x // CELL_SIZE),
        )
