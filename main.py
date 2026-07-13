# /// script
# dependencies = [
#     "numpy",
#     "pygame-ce",
#     "pygame-textinput",
# ]
# ///

import numpy as np
import sys
import pygame
import asyncio
from mazegenerator.mazegenerator import MazeGenerator
from src.frontend.controller import Controller
from src.backend.logic import GameLogic
from src.backend.parse_config_files import parse_game_config
from src.state import GameConfig


async def main() -> None:
    is_wasm = sys.platform == "emscripten"

    if is_wasm:
        config_path = "config.txt"
    else:
        if len(sys.argv) == 1:
            print("'config.txt' file missing")
            return
        if len(sys.argv) > 2:
            print("Only single 'config.txt' file allowed")
            return
        config_path = sys.argv[1]
    config_data = parse_game_config(config_path)
    config = GameConfig(**config_data)
    gen = MazeGenerator(
        size=(config.maze_width, config.maze_height), seed=42)
    logic = GameLogic(gen, config)
    controller = Controller(logic)
    controller.set_running_status(True)
    controller.start_background_music()
    while controller.running:
        controller.run_single_scene()
        await asyncio.sleep(0)
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
