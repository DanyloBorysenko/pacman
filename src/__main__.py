from mazegenerator.mazegenerator import MazeGenerator
from src.controller import Controller
from src.state import GameState


def main() -> None:
    gen = MazeGenerator()
    state = GameState(gen.maze)
    controller = Controller(state)
    controller.run()


if __name__ == "__main__":
    main()
