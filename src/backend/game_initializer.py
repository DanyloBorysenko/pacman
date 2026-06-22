import numpy as np
import enum
from random import random
from typing import List, Tuple
from ..state import GameState


GUM_PROBABILITY = 0.8
WALL_MASK = 15
PACGUM = 16
SUPER_PACGUM = 32


def find_valid_center(maze: np.ndarray) -> Tuple[int, int]:
    height, width = maze.shape

    ideal_y = height // 2
    ideal_x = width // 2

    # Simple outward expansion logic
    found = False
    valid_y, valid_x = ideal_y, ideal_x

    # We increase the radius step by step (0, 1, 2, 3 tiles away from center)
    for radius in range(max(height, width)):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # We only look at coordinates exactly at the current radius boundary
                if abs(dy) + abs(dx) == radius:
                    test_y = ideal_y + dy
                    test_x = ideal_x + dx
                    
                    # Make sure we don't look outside the array boundaries
                    if 0 <= test_y < height and 0 <= test_x < width:
                        # Check if it's a valid walkable corridor
                        if (self.game_state.maze[test_y, test_x] & WALL_MASK) < 15:
                            valid_y = test_y
                            valid_x = test_x
                            found = True
                            break
            if found:
                break
        if found:
            break
    return valid_y, valid_x


class GameInitializer:
	def __init__(self, game_state: GameState):
        self.game_state = game_state
        if not isinstance(game_state.maze, np.ndarray):
            self.game_state.maze = np.array(game_state.maze)
        self._get_valid_center_and_corners()
    
    def _get_valid_center_and_corners(self) -> None:
        self.corners = [
			(0, 0),
			(0, self.game_state.maze.shape[1] - 1),
			(self.game_state.maze.shape[0] - 1, 0),
			(self.game_state.maze.shape[0] - 1, self.game_state.maze.shape[1] - 1),
			]
        self.valid_center = find_valid_center(self.game_state.maze)

	def _place_pacgums(self) -> None:
        total_pacgums = self.game_state.config.pacgum
        is_valid_corridors = (self.game_state.maze & WALL_MASK) < 15
        is_valid_corridors[self.valid_center[0], self.valid_center[1]] = False

        valid_indices = np.argwhere(is_valid_corridors)
        num_to_select = min(total_pacgums, len(valid_indices))

        chosen_row_indices = np.random.choice(len(valid_indices), size=num_to_select, replace=False)
        chosen_coordinates = valid_indices[chosen_row_indices]
        self.game_state.maze[chosen_coordinates[:, 0], chosen_coordinates[:, 1]] |= PACGUM
	
	def _place_super_pacgums(self) -> None:
        for y, x in self.corners:
            self.game_state.maze[y, x] &= ~PACGUM
            self.game_state.maze[y, x] |= SUPER_PACGUM
	
	def _place_ghosts(self) -> None:
        self.game_state.ghosts[0].x, self.game_state.ghosts[0].y = 0, 0
        self.game_state.ghosts[1].x, self.game_state.ghosts[1].y = 0, self.game_state.maze.shape[1] - 1
        self.game_state.ghosts[2].x, self.game_state.ghosts[2].y = self.game_state.maze.shape[0] - 1, 0
        self.game_state.ghosts[3].x, self.game_state.ghosts[3].y = self.game_state.maze.shape[0] - 1, self.game_state.maze.shape[1] - 1

    def _get_valid_center(self) -> None:
        yc, xc = self.game_state.maze.shape[0] // 2, self.game_state.maze.shape[1] // 2
        if self.game_state.maze[yc, xc] < 15:
            return yx, xc

    def _place_pacman(self) -> None:
        self.game_state.pacman.y, self.game_state.pacman.x = self.valid_center[0], self.valid_center[1]

