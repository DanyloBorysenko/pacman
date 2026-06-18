from mazegenerator.mazegenerator import MazeGenerator
from src.controller import Controller


def main() -> None:
    gen = MazeGenerator()
    controller = Controller(gen.maze)
    controller.run()

if __name__ == "__main__":
    main()
