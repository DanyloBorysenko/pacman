from abc import ABC, abstractmethod
import numpy as np
from ..state import GameState, BitMaps

class GameAction(ABC):
    @abstractmethod
    def execute(self, state: GameState) -> None:
        """Process a isolated rule change on the game state."""
        pass

# --- Module 1: Item Consumption ---
class ConsumeItemsAction(GameAction):
    def execute(self, state: GameState) -> None:
        pacman = state.pacman
        # We look at the grid where Pac-Man currently is
        y, x = int(pacman.y), int(pacman.x)
        current_tile = state.maze[y, x]

        if current_tile & BitMaps.PACGUM:
            state.live_status.current_score += state.config.points_per_pacgum
            state.maze[y, x] &= ~BitMaps.PACGUM
        elif current_tile & BitMaps.SUPER_PACGUM:
            state.live_status.current_score += state.config.points_per_super_pacgum
            state.maze[y, x] &= ~BitMaps.SUPER_PACGUM
            for ghost in state.ghosts:
                ghost.is_edible = True
                ghost.colour = "blue"
                ghost.time_laps = 0

# --- Module 2: Level Clear Checking ---
class CheckLevelClearAction(GameAction):
    def __init__(self, advancer_callback):
        self.advance_level = advancer_callback

    def execute(self, state: GameState) -> None:
        if not np.any(state.maze & (BitMaps.SUPER_PACGUM | BitMaps.PACGUM)):
            self.advance_level() # Call back to manager to load next map