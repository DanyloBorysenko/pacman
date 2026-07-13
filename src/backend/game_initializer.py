import numpy as np
from typing import Tuple
from ..state import GameState, BitMaps, GameStats


class GameInitializer:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        if not isinstance(self.game_state.maze, np.ndarray):
            self.game_state.maze = np.array(self.game_state.maze)

    def initialize(self) -> None:
        self._get_valid_center_and_corners()
        self._place_pacgums()
        self._place_super_pacgums()
        self._place_ghosts()
        self._place_pacman()
        self.game_state.live_status = GameStats(
            lives_remain=self.game_state.config.lives,
            time_left=self.game_state.config.level_max_time,
            pacman_curr_spd=self.game_state.config.pacman_speed,
            ghost_curr_speed=self.game_state.config.ghost_speed)

    def reload_new_level_map(self, game_state: GameState) -> None:
        from mazegenerator.mazegenerator import MazeGenerator
        generator = MazeGenerator(
            size=(self.game_state.config.maze_width,
                  self.game_state.config.maze_height))

        game_state.maze = np.array(generator.maze)
        self.game_state = game_state
        self._get_valid_center_and_corners()
        self._place_pacgums()
        self._place_super_pacgums()
        self._place_ghosts()
        self._place_pacman()
        self.game_state.live_status.time_left =\
            self.game_state.config.level_max_time

    def _get_valid_center_and_corners(self) -> None:
        self.corners = [
            (0, 0),
            (0, self.game_state.maze.shape[1] - 1),
            (self.game_state.maze.shape[0] - 1, 0),
            (self.game_state.maze.shape[0] - 1,
                self.game_state.maze.shape[1] - 1),
            ]
        self.valid_center = self.find_valid_center(self.game_state.maze)

    def _place_pacgums(self) -> None:
        total_pacgums = self.game_state.config.pacgum
        is_valid_corridors = (self.game_state.maze & BitMaps.WALL_MASK) < 15

        is_valid_corridors[self.valid_center[0], self.valid_center[1]] = False
        for y, x in self.corners:
            is_valid_corridors[y, x] = False

        valid_indices = np.argwhere(is_valid_corridors)
        num_to_select = min(total_pacgums, len(valid_indices))

        chosen_row_indices = np.random.choice(
            len(valid_indices), size=num_to_select, replace=False)
        chosen_coordinates = valid_indices[chosen_row_indices]
        self.game_state.maze[
            chosen_coordinates[:, 0], chosen_coordinates[:, 1]] |=\
            BitMaps.PACGUM

    def _place_super_pacgums(self) -> None:
        for y, x in self.corners:
            self.game_state.maze[y, x] &= ~BitMaps.PACGUM
            self.game_state.maze[y, x] |= BitMaps.SUPER_PACGUM

    def _place_ghosts(self) -> None:
        self.game_state.ghosts[0].y, self.game_state.ghosts[0].x = 0, 0
        self.game_state.ghosts[1].y, self.game_state.ghosts[1].x =\
            0, self.game_state.maze.shape[1] - 1
        self.game_state.ghosts[2].y, self.game_state.ghosts[2].x =\
            self.game_state.maze.shape[0] - 1, 0
        self.game_state.ghosts[3].y, self.game_state.ghosts[3].x =\
            self.game_state.maze.shape[0] - 1, \
            self.game_state.maze.shape[1] - 1
        self.game_state.ghosts[0].home_y, \
            self.game_state.ghosts[0].home_x = 0, 0
        self.game_state.ghosts[1].home_y, self.game_state.ghosts[1].home_x =\
            0, self.game_state.maze.shape[1] - 1
        self.game_state.ghosts[2].home_y, self.game_state.ghosts[2].home_x =\
            self.game_state.maze.shape[0] - 1, 0
        self.game_state.ghosts[3].home_y, self.game_state.ghosts[3].home_x =\
            self.game_state.maze.shape[0] - 1, \
            self.game_state.maze.shape[1] - 1

    def _place_pacman(self) -> None:
        self.game_state.pacman.y, self.game_state.pacman.x =\
            self.valid_center[0], self.valid_center[1]
        self.game_state.pacman.start_x = self.valid_center[1]
        self.game_state.pacman.start_y = self.valid_center[0]

    @staticmethod
    def find_valid_center(maze: np.ndarray) -> Tuple[int, int]:
        height, width = maze.shape

        ideal_y = height // 2
        ideal_x = width // 2

        # Simple outward expansion logic
        found = False
        valid_y, valid_x = ideal_y, ideal_x

        # We increase the radius step by step
        # (0, 1, 2, 3 tiles away from center)
        for radius in range(max(height, width)):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    # We only look at coordinates exactly at
                    # the current radius boundary
                    if abs(dy) + abs(dx) == radius:
                        test_y = ideal_y + dy
                        test_x = ideal_x + dx

                        # Make sure we don't look outside the array boundaries
                        if 0 <= test_y < height and 0 <= test_x < width:
                            # Check if it's a valid walkable corridor
                            if (maze[test_y, test_x] & BitMaps.WALL_MASK) < 15:
                                valid_y = test_y
                                valid_x = test_x
                                found = True
                                break
                if found:
                    break
            if found:
                break
        return valid_y, valid_x
