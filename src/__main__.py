from mazegenerator.mazegenerator import MazeGenerator
from src.controller import Controller
from src.state import GameState, Position


def main() -> None:
    gen = MazeGenerator()
    state = GameState(
        maze=gen.maze,
        pacman=Position(0, 0))
    controller = Controller(state)
    controller.run()


if __name__ == "__main__":
    main()
