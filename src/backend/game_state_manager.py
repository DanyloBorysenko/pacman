from typing import Tuple
from ..state import GameState, Direction, BitMaps

# Instead of tile jumps, use tiny fractions per frame
PACMAN_SPEED = 0.1  # Moves 1/10th of a tile per loop tick
GHOST_SPEED = 0.1


class GameStateManager:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        # Keep track of current actual velocity
        self.current_direction = (0, 0)

    def request_move(self, direction: Direction) -> None:
        """Called when a user presses a key."""
        # 1. For a smooth turn, we usually check if Pac-Man is *exactly* at a grid tile junction
        # or close enough to snap to it.
        curr_x = self.game_state.pacman.x
        curr_y = self.game_state.pacman.y
        
        # Check alignment: If he is roughly at an integer coordinate (e.g., 4.0, 2.0)
        if abs(curr_x - round(curr_x)) < 0.01 and abs(curr_y - round(curr_y)) < 0.01:
            tile_y = int(round(curr_y))
            tile_x = int(round(curr_x))
            curr_tile = self.game_state.maze[tile_y, tile_x]
            
            # Check if the requested direction is open
            if self._is_move_allowed(curr_tile, direction):
                self.current_direction = direction.value

    def _is_move_allowed(self, curr_tile: int, direction: Direction) -> bool:
        if direction == Direction.RIGHT and (curr_tile & BitMaps.EAST):
            return False
        elif direction == Direction.LEFT and (curr_tile & BitMaps.WEST):
            return False
        elif direction == Direction.UP and (curr_tile & BitMaps.NORTH):
            return False
        elif direction == Direction.DOWN and (curr_tile & BitMaps.SOUTH):
            return False
        return True

    def update_tick(self) -> None:
        """This gets called once per frame by your main engine clock loop."""
        # 1. Get current position
        curr_x = self.game_state.pacman.x
        curr_y = self.game_state.pacman.y
        
        # 2. Before applying fractional movement, check if the tile directly ahead is a wall
        # Only check when approaching a new tile boundary
        next_x = curr_x + self.current_direction[0] * PACMAN_SPEED
        next_y = curr_y + self.current_direction[1] * PACMAN_SPEED
        
        # Look ahead calculation
        if self.current_direction != (0, 0):
            # Find the tile index Pac-Man is walking towards
            target_tile_x = int(next_x + 0.5 if self.current_direction[0] > 0 else next_x)
            target_tile_y = int(next_y + 0.5 if self.current_direction[1] > 0 else next_y)
            
            # # Safety check layout constraints
            # if 0 <= target_tile_y < self.game_state.maze.shape[0] and 0 <= target_tile_x < self.game_state.maze.shape[1]:
            #     # If a wall blocks the current direction, stop him dead center
            #     # By checking our bitmasks against the current tile
            #     curr_tile = self.game_state.maze[int(curr_y), int(curr_x)]
            #     if self.current_direction == (1, 0) and (curr_tile & BitMaps.EAST):
            #         self.current_direction = (0, 0)
            #     elif self.current_direction == (-1, 0) and (curr_tile & BitMaps.WEST):
            #         self.current_direction = (0, 0)
            #     elif self.current_direction == (0, -1) and (curr_tile & BitMaps.NORTH):
            #         self.current_direction = (0, 0)
            #     elif self.current_direction == (0, 1) and (curr_tile & BitMaps.SOUTH):
            #         self.current_direction = (0, 0)

        # 3. Apply fractional movement velocity safely
        self.game_state.pacman.x += self.current_direction[0] * PACMAN_SPEED
        self.game_state.pacman.y += self.current_direction[1] * PACMAN_SPEED

        # 4. Check items based on closest integer coordinate position
        map_x = int(round(self.game_state.pacman.x))
        map_y = int(round(self.game_state.pacman.y))
        new_tile = self.game_state.maze[map_y, map_x]

        if (new_tile & BitMaps.PACGUM):
            self.game_state.live_status.current_score += self.game_state.config.points_per_pacgum.value
            self.game_state.maze[map_y, map_x] &= ~BitMaps.PACGUM
        elif (new_tile & BitMaps.SUPER_PACGUM):
            self.game_state.live_status.current_score += self.game_state.config.points_per_super_pacgum.value
            self.game_state.maze[map_y, map_x] &= ~BitMaps.SUPER_PACGUM