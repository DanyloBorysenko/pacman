from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple, List
import random
import math
from ..state import BitMaps, Direction


class GhostMovementStrategy(ABC):
    """Abstract base class establishing the contract for all Ghost AI behaviors."""

    @abstractmethod
    def get_next_move(self, current_pos: Tuple[int, int], maze: np.ndarray, pacman_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calculate the next target step vector (dx, dy).

        :param current_pos: (y, x) integer grid coordinates of the ghost.
        :param maze: The current NumPy array game board.
        :param pacman_pos: (y, x) integer grid coordinates of Pac-Man (for tracking).
        :return: A direction tuple (dx, dy) representing the chosen move.
        """
        pass

    def _get_valid_directions(self, current_pos: Tuple[int, int],
                              maze: np.ndarray) -> List[Tuple[int, int]]:
        """Helper utility shared by all ghosts to scan unblocked paths around them."""
        y, x = current_pos
        val = maze[y, x]
        valid_moves = []

        # Bitmask direction vectors: (dx, dy)
        if not (val & BitMaps.NORTH):
            valid_moves.append(Direction.UP.value)
        if not (val & BitMaps.EAST):
            valid_moves.append(Direction.RIGHT.value)
        if not (val & BitMaps.SOUTH):
            valid_moves.append(Direction.DOWN.value)
        if not (val & BitMaps.WEST):
            valid_moves.append(Direction.LEFT.value)

        return valid_moves if valid_moves else [(0, 0)] # Fallback if trapped


class RandomMovement(GhostMovementStrategy):
    """Ghost moves completely randomly at every junction."""

    def get_next_move(
            self, current_pos: Tuple[int, int],
            maze: np.ndarray, pacman_pos: Tuple[int, int]
            ) -> Tuple[int, int]:
        valid_moves = self._get_valid_directions(current_pos, maze)
        return random.choice(valid_moves)


class DirectionalMovement(GhostMovementStrategy):
    """Aggressive ghost that always picks the path bringing it closest to Pac-Man."""

    def get_next_move(
            self, current_pos: Tuple[int, int],
            maze: np.ndarray, pacman_pos: Tuple[int, int]
            ) -> Tuple[int, int]:
        valid_moves = self._get_valid_directions(current_pos, maze)
        y, x = current_pos
        target_y, target_x = pacman_pos

        best_move = valid_moves[0]
        min_distance = float('inf')

        for dx, dy in valid_moves:
            # Simulate where this step would put the ghost
            next_x = x + dx
            next_y = y + dy

            # Distance formula to target
            # dist = math.sqrt((next_x - target_x)**2 + (next_y - target_y)**2)
            dist = abs(next_x - target_x) + abs(next_y - target_y)

            if dist < min_distance:
                min_distance = dist
                best_move = (dx, dy)

        return best_move


class PseudoRandomMovement(GhostMovementStrategy):
    """Chases Pac-Man with high probability, but occasionally takes a random turn."""

    def __init__(self, chase_probability: float = 0.7):
        self.chase_probability = chase_probability
        self._chaser = DirectionalMovement()
        self._randomizer = RandomMovement()

    def get_next_move(self, current_pos: Tuple[int, int],
            maze: np.ndarray, pacman_pos: Tuple[int, int]) -> Tuple[int, int]:
        # Generate a seed value between 0.0 and 1.0
        if random.random() < self.chase_probability:
            return self._chaser.get_next_move(current_pos, maze, pacman_pos)
        else:
            return self._randomizer.get_next_move(current_pos, maze, pacman_pos)
