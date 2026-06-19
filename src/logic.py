from src.state import GameState, Position
from mazegenerator.mazegenerator import MazeGenerator


class GameLogic:
    def __init__(self, generator: MazeGenerator):
        self.generator = generator

    def create_default_state(self) -> GameState:
        state = GameState(
            maze=self.generator.maze,
            pacman=Position(0, 0))
        return state
