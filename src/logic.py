from src.state import GameState, Pacman, Direction
from mazegenerator.mazegenerator import MazeGenerator
from src.constants import CELL_SIZE

PACMAN_SPEED = 100


class GameLogic:
    def __init__(self, generator: MazeGenerator):
        self.generator = generator
        self.maze = generator.maze

    def create_default_state(self) -> GameState:
        state = GameState(
            maze=self.maze,
            pacman=Pacman(5 * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2, None))
        return state

    def update(self, state: GameState, dt: float) -> None:
        pacman = state.pacman
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

    def _pacman_cell(self, pacman: Pacman) -> tuple[int, int]:
        return (
            int(pacman.y // CELL_SIZE),
            int(pacman.x // CELL_SIZE),
        )
