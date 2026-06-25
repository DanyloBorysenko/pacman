from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple, List
import random
import math


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

    def _get_valid_directions(self, current_pos: Tuple[int, int], maze: np.ndarray) -> List[Tuple[int, int]]:
        """Helper utility shared by all ghosts to scan unblocked paths around them."""
        y, x = current_pos
        val = maze[y, x]
        valid_moves = []

        # Bitmask direction vectors: (dx, dy)
        # Assuming constants: NORTH=1, EAST=2, SOUTH=4, WEST=8 (based on your layout fix)
        if not (val & 1):  # NORTH open
            valid_moves.append((0, -1))
        if not (val & 2):  # EAST open
            valid_moves.append((1, 0))
        if not (val & 4):  # SOUTH open
            valid_moves.append((0, 1))
        if not (val & 8):  # WEST open
            valid_moves.append((-1, 0))

        return valid_moves if valid_moves else [(0, 0)] # Fallback if trapped
    

class RandomMovement(GhostMovementStrategy):
    """Ghost moves completely randomly at every junction."""

    def get_next_move(self, current_pos: Tuple[int, int], maze: np.ndarray, pacman_pos: Tuple[int, int]) -> Tuple[int, int]:
        valid_moves = self._get_valid_directions(current_pos, maze)
        return random.choice(valid_moves)
    

class DirectionalMovement(GhostMovementStrategy):
    """Aggressive ghost that always picks the path bringing it closest to Pac-Man."""

    def get_next_move(self, current_pos: Tuple[int, int], maze: np.ndarray, pacman_pos: Tuple[int, int]) -> Tuple[int, int]:
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
            dist = math.sqrt((next_x - target_x)**2 + (next_y - target_y)**2)
            
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

    def get_next_move(self, current_pos: Tuple[int, int], maze: np.ndarray, pacman_pos: Tuple[int, int]) -> Tuple[int, int]:
        # Generate a seed value between 0.0 and 1.0
        if random.random() < self.chase_probability:
            return self._chaser.get_next_move(current_pos, maze, pacman_pos)
        else:
            return self._randomizer.get_next_move(current_pos, maze, pacman_pos)
        
    
# Inside your Engine Setup
self.game_state.ghosts[0].strategy = DirectionalMovement()     # Aggressive Red
self.game_state.ghosts[1].strategy = PseudoRandomMovement(0.8) # Smart Pink
self.game_state.ghosts[2].strategy = PseudoRandomMovement(0.5) # Unpredictable Cyan
self.game_state.ghosts[3].strategy = RandomMovement()         # Wandering Orange

# Then, your move_ghosts loop becomes a clean one-liner:
def move_ghosts(self):
    for ghost in self.game_state.ghosts:
        current_coords = (int(ghost.y), int(ghost.x))
        pacman_coords = (int(self.game_state.pacman.y), int(self.game_state.pacman.x))
        
        dx, dy = ghost.strategy.get_next_move(current_coords, self.game_state.maze, pacman_coords)
        
        ghost.x += dx * ghost.speed
        ghost.y += dy * ghost.speed