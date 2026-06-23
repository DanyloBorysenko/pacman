from src.state import GameState, Pacman, Direction, Ghost
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
            pacman=Pacman(
                5 * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2, None),
            ghosts=[Ghost(3 * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2, None, "red"), Ghost(8 * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2, None, "red")])
        return state

    def update(self, state: GameState, dt: float) -> None:
        if state.paused:
            return
        pacman = state.pacman
        pacman.mouth_phase += dt * 8
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
