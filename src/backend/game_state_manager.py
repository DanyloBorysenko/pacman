from typing import Tuple
import math
from ..state import GameState, Direction, BitMaps

# Speeds are now explicitly: Grid Tiles Per Second
PACMAN_SPEED = 2.0
GHOST_SPEED = 4.0


class GameStateManager:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def update(self, dt: float, requested_direction: Direction) -> None:
        """The central heartbeat tick. Pass dt here from your main clock loop."""
        pacman = self.game_state.pacman

        # 1. Initialize destination coordinates if they are unassigned (-1 baseline setup)
        if pacman.xd == -1 and pacman.yd == -1:
            if requested_direction is None:
                return
            curr_x = int(pacman.x)
            curr_y = int(pacman.y)
            curr_tile = self.game_state.maze[curr_y, curr_x]

            if self._is_move_allowed(curr_tile, requested_direction):
                pacman.assigned_direction = requested_direction
                pacman.xd = curr_x + requested_direction.value[0]
                pacman.yd = curr_y + requested_direction.value[1]
            else:
                return

        # 2. Process real-time fractional displacement progress using dt
        self._move_towards_target(dt, requested_direction)

    def _move_towards_target(self, dt: float, requested_direction: Direction) -> None:
        pacman = self.game_state.pacman
        direction = pacman.assigned_direction

        if direction is None:
            return

        # Calculate remaining geometric path distance to the target destination tile
        dx = pacman.xd - pacman.x
        dy = pacman.yd - pacman.y
        distance_to_target = math.sqrt(dx**2 + dy**2)

        # Determine how large of a step Pac-Man can physically take over this temporal frame
        step_size = PACMAN_SPEED * dt

        # CHECK ARRIVAL: If our step covers or passes the target distance
        if step_size >= distance_to_target:
            # Snap position completely to prevent floating point drift lines
            pacman.x = float(pacman.xd)
            pacman.y = float(pacman.yd)

            # Arrived! Process consumption rules on this newly claimed tile coordinate
            self._consume_items(int(pacman.y), int(pacman.x))

            # Evaluate where to route next based on the user's latest steering inputs
            curr_tile = self.game_state.maze[int(pacman.y), int(pacman.x)]

            if requested_direction and self._is_move_allowed(curr_tile, requested_direction):
                # Turn successful! Set up the next adjacent target tile layout
                pacman.assigned_direction = requested_direction
                pacman.xd = int(pacman.x) + requested_direction.value[0]
                pacman.yd = int(pacman.y) + requested_direction.value[1]
            elif self._is_move_allowed(curr_tile, pacman.assigned_direction):
                # No new turn requested, continue straight ahead toward next tile line
                pacman.xd = int(pacman.x) + pacman.assigned_direction.value[0]
                pacman.yd = int(pacman.y) + pacman.assigned_direction.value[1]
            else:
                # Path dead end: Reset tracking markers back to standstill mode
                pacman.xd = -1
                pacman.yd = -1
                pacman.assigned_direction = None
        else:
            # CONTINUOUS GLIDE: We haven't reached the node intersection yet, advance tracking positions
            pacman.x += direction.value[0] * step_size
            pacman.y += direction.value[1] * step_size

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

    def _consume_items(self, y: int, x: int) -> None:
        """Handles eating mechanics precisely upon clean destination arrivals."""
        current_tile = self.game_state.maze[y, x]

        if current_tile & BitMaps.PACGUM:
            self.game_state.live_status.current_score += self.game_state.config.points_per_pacgum.value
            self.game_state.maze[y, x] &= ~BitMaps.PACGUM
        elif current_tile & BitMaps.SUPER_PACGUM:
            self.game_state.live_status.current_score += self.game_state.config.points_per_super_pacgum.value
            self.game_state.maze[y, x] &= ~BitMaps.SUPER_PACGUM