import math
from typing import Tuple, Optional, Callable
from ..state import Direction, GameState


class GridMover:
    """Handles pure directional target-seeking mechanics for
    grid-based entities."""

    @staticmethod
    def advance_towards_target(
        current_x: float,
        current_y: float,
        target_xd: int,
        target_yd: int,
        direction: Optional[Tuple[int, int]], 
        speed: float,
        dt: float
    ) -> Tuple[float, float, bool]:
        """
        Calculates the next fractional step position.
        Returns (new_x, new_y, arrived_status_boolean).
        """
        if target_xd == -1 or target_yd == -1 or direction is None:
            return current_x, current_y, True

        dx = target_xd - current_x
        dy = target_yd - current_y
        distance_to_target = math.sqrt(dx**2 + dy**2)
        step_size = speed * dt

        if step_size >= distance_to_target:
            return float(target_xd), float(target_yd), True

        new_x = current_x + direction[0] * step_size
        new_y = current_y + direction[1] * step_size
        return new_x, new_y, False


class PacmanMovementController:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def update(
            self, dt: float, requested_direction: Direction
            ) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Updates Pacman's position. 
        Returns (arrived_at_new_tile, tile_coordinates_if_arrived).
        """
        pacman = self.game_state.pacman

        # 1. Bootstrap target assignments if unassigned
        if pacman.xd == -1 and pacman.yd == -1:
            if requested_direction is None:
                return False, None
            if self._is_move_allowed(requested_direction):
                pacman.assigned_direction = requested_direction
                pacman.xd = int(pacman.x) + requested_direction.value[0]
                pacman.yd = int(pacman.y) + requested_direction.value[1]
            else:
                return False, None

        # 2. Compute fractional frame step via our core shared Mover component
        new_x, new_y, arrived = GridMover.advance_towards_target(
            pacman.x, pacman.y, pacman.xd, pacman.yd,
            pacman.assigned_direction.value if pacman.assigned_direction else None,
            self.game_state.live_status.pacman_curr_spd, dt
        )
        pacman.x, pacman.y = new_x, new_y

        # 3. Handle junction arrival and queue next paths
        if arrived and pacman.assigned_direction:
            arrival_coords = (int(pacman.y), int(pacman.x))

            if requested_direction and self._is_move_allowed(
                    requested_direction):
                pacman.assigned_direction = requested_direction
                pacman.xd = int(pacman.x) + requested_direction.value[0]
                pacman.yd = int(pacman.y) + requested_direction.value[1]
            elif self._is_move_allowed(pacman.assigned_direction):
                pacman.xd = int(pacman.x) + pacman.assigned_direction.value[0]
                pacman.yd = int(pacman.y) + pacman.assigned_direction.value[1]
            else:
                pacman.xd, pacman.yd = -1, -1
                pacman.assigned_direction = Direction.UP

            return True, arrival_coords

        return False, None

    def _is_move_allowed(self, direction: Direction) -> bool:
        from ..state import BitMaps
        curr_tile = self.game_state.maze[
            int(self.game_state.pacman.y), int(self.game_state.pacman.x)]
        mapping = {
            Direction.RIGHT: BitMaps.EAST, Direction.LEFT: BitMaps.WEST,
            Direction.UP: BitMaps.NORTH, Direction.DOWN: BitMaps.SOUTH
        }
        return not bool(curr_tile & mapping[direction])


class GhostMovementController:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def update(self, dt: float) -> None:
        if self.game_state.cheat_freeze:
            return

        pacman_coords = (int(self.game_state.pacman.y),
                         int(self.game_state.pacman.x))

        for ghost in self.game_state.ghosts:
            if ghost.is_dead:
                continue

            # 1. Bootstrap: Target initialization
            if ghost.xd == -1 and ghost.yd == -1:
                # print(ghost.assigned_direction, ghost.strategy)
                dx, dy = ghost.strategy.get_next_move(
                    (int(ghost.y), int(ghost.x)), self.game_state.maze,
                    pacman_coords, ghost.assigned_direction, ghost.is_edible
                )
                ghost.assigned_direction = (dx, dy)
                ghost.xd = int(ghost.x) + dx
                ghost.yd = int(ghost.y) + dy

            # 2. Advance positions via core Mover component
            new_x, new_y, arrived = GridMover.advance_towards_target(
                ghost.x, ghost.y, ghost.xd, ghost.yd,
                ghost.assigned_direction,
                self.game_state.live_status.ghost_curr_speed, dt
            )
            ghost.x, ghost.y = new_x, new_y

            # 3. Junction checking: Query AI behavior for the next path
            if arrived and ghost.assigned_direction:
                dx, dy = ghost.strategy.get_next_move(
                    (int(ghost.y), int(ghost.x)), self.game_state.maze,
                    pacman_coords, ghost.assigned_direction, ghost.is_edible
                )
                ghost.assigned_direction = (dx, dy)
                ghost.xd = int(ghost.x) + dx
                ghost.yd = int(ghost.y) + dy
