from mazegenerator.mazegenerator import MazeGenerator
from src.frontend.controller import Controller
from src.logic import GameLogic


def main() -> None:
    gen = MazeGenerator()
    logic = GameLogic(gen)
    controller = Controller(logic)
    controller.run()


if __name__ == "__main__":
    main()
