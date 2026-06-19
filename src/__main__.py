from mazegenerator.mazegenerator import MazeGenerator
from src.controller import Controller
from src.logic import GameLogic


def main() -> None:
    gen = MazeGenerator()
    logic = GameLogic(gen)
    state = logic.create_default_state()
    controller = Controller(state, logic)
    controller.run()


if __name__ == "__main__":
    main()
