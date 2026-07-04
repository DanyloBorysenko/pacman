import sys
from mazegenerator.mazegenerator import MazeGenerator
from src.frontend.controller import Controller
from src.backend.logic import GameLogic
from src.backend.parse_config_files import parse_game_config
from src.state import GameConfig


def main() -> None:
    if len(sys.argv) == 1:
        print("'config.txt' file missing")
        return
    if len(sys.argv) > 2:
        print("Only single 'config.txt' file allowed")
        return
    config_data = parse_game_config(sys.argv[1])
    config = GameConfig(**config_data)
    gen = MazeGenerator(size=(15, 15), seed=42)
    logic = GameLogic(gen, config)
    controller = Controller(logic)
    controller.run()


if __name__ == "__main__":
    main()
