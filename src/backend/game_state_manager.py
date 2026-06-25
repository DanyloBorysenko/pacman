from typing import Tuple
import math
import time
from ..state import GameState, Direction, BitMaps, Ghost

# Speeds are now explicitly: Grid Tiles Per Second
PACMAN_SPEED = 4.0
GHOST_SPEED = 3.5


class GameStateManager:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def update_pacman(self, dt: float, requested_direction: Direction) -> None:
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

    def _move_towards_target(
            self, dt: float,
            requested_direction: Direction
            ) -> None:
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
            print(f"Score: {self.game_state.live_status.current_score}")
        elif current_tile & BitMaps.SUPER_PACGUM:
            self.game_state.live_status.current_score += self.game_state.config.points_per_super_pacgum.value
            self.game_state.maze[y, x] &= ~BitMaps.SUPER_PACGUM
            for ghost in self.game_state.ghosts:
                ghost.is_edible = True
                ghost.colour = "blue"
                ghost.edible_since = time.time()
                ghost.time_laps = 0
            print(f"Score: {self.game_state.live_status.current_score}")

    def update_ghosts(self, dt: float) -> None:
        """Updates all ghosts using fractional time slices and coordinates their AI changes."""
        pacman_coords = (int(self.game_state.pacman.y), int(self.game_state.pacman.x))

        for ghost in self.game_state.ghosts:
            if ghost.is_edible:
                # print(f"Ghost edible, time laps: {ghost.time_laps}")
                ghost.time_laps += dt
                if ghost.time_laps >= self.game_state.config.ghost_edible_time.value:
                    ghost.is_edible = False
                    ghost.time_laps = 0
                    ghost.colour = ghost.initial_colour

            # 1. Bootstrapping: Initialize targets if they are fresh out of spawn (-1 baseline setup)
            if ghost.xd == -1 and ghost.yd == -1:
                curr_x = int(ghost.x)
                curr_y = int(ghost.y)
                curr_coords = (curr_y, curr_x)

                # Fetch direction vector from the ghost's movement
                dx, dy = ghost.strategy.get_next_move(
                    curr_coords, self.game_state.maze,
                    pacman_coords, ghost.assigned_direction,
                    ghost.is_edible)
                ghost.assigned_direction = (dx, dy)
                ghost.xd = curr_x + dx
                ghost.yd = curr_y + dy

            # 2. Track distance to target
            dgx = ghost.xd - ghost.x
            dgy = ghost.yd - ghost.y
            distance_to_target = math.sqrt(dgx**2 + dgy**2)

            # Ghosts can have different speeds based on configuration or states (e.g. slowed down when frightened)
            step_size = GHOST_SPEED * dt

            # 3. CHECK ARRIVAL
            if step_size >= distance_to_target:
                # Snap ghost perfectly to tile junction intersection
                ghost.x = float(ghost.xd)
                ghost.y = float(ghost.yd)

                # We have landed! Ask the AI strategy for the next step vector
                curr_coords = (int(ghost.y), int(ghost.x))
                dx, dy = ghost.strategy.get_next_move(
                    curr_coords, self.game_state.maze, pacman_coords,
                    ghost.assigned_direction, ghost.is_edible)

                # Update assignments for the next track step segment
                ghost.assigned_direction = (dx, dy)
                ghost.xd = int(ghost.x) + dx
                ghost.yd = int(ghost.y) + dy
            else:
                # 4. CONTINUOUS GLIDE
                vec = ghost.assigned_direction
                if vec:
                    ghost.x += vec[0] * step_size
                    ghost.y += vec[1] * step_size


    def check_collisions(self) -> None:
        """Evaluates proximity between Pac-Man and all ghosts, triggering state updates."""
        pacman = self.game_state.pacman

        for i, ghost in enumerate(self.game_state.ghosts):
            # 1. Calculate distance between Pac-Man and the current ghost
            distance = math.sqrt((pacman.x - ghost.x)**2 + (pacman.y - ghost.y)**2)

            # 2. Threshold collision check (closer than half a tile)
            if distance < 0.5:

                # STEP B: Ghost is Frightened (Edible)
                if ghost.is_edible:
                    print(f"ghost is eaten, time laps: {ghost.time_laps}")
                    self._process_ghost_eaten(ghost, i)

                # STEP A: Ghost is Dangerous
                else:
                    self._process_player_death()
                    break  # Stop checking other ghosts on this frame since player died

    def _process_ghost_eaten(self, ghost: Ghost, ghost_index: int) -> None:
        """Handles Step B: Pac-Man devours an edible ghost."""
        # 1. Award points dynamically from config
        self.game_state.live_status.current_score += self.game_state.config.points_per_ghost.value

        # 2. Reset this specific ghost's state flags
        ghost.is_edible = False
        ghost.time_laps = 0
        ghost.colour = ghost.initial_colour

        # 3. Teleport the ghost back to its starting coordinate layout
        # (Assuming your state handles individual home corners)
        ghost.x = float(ghost.home_x)
        ghost.y = float(ghost.home_y)

        # 4. Reset its GridMover targets so it doesn't try to glide back outwards sideways
        ghost.xd = -1
        ghost.yd = -1
        # time.sleep(1)

    def _process_player_death(self) -> None:
        """Handles Step A: Player loses a life to a dangerous ghost."""
        # 1. Deduct life status
        self.game_state.live_status.lives_remain -= 1
        print(f"live remains: {self.game_state.live_status.lives_remain}")

        # 2. Check for game over state transition
        if self.game_state.live_status.lives_remain <= 0:
            self.game_state.current_screen = "GAME_OVER"
            self.game_state.paused = True
        else:
            # 3. Respawn Pac-Man at the map's safe starting center
            self.game_state.pacman.x = float(self.game_state.pacman.start_x)
            self.game_state.pacman.y = float(self.game_state.pacman.start_y)

            # 4. Clear Pac-Man's GridMover destination states
            self.game_state.pacman.xd = -1
            self.game_state.pacman.yd = -1
            self.game_state.pacman.assigned_direction = None

            # 5. Optional Peer Tip: Reset all ghosts to their homes on death 
            # to prevent instant spawn-killing when Pac-Man reappears!
            for i, ghost in enumerate(self.game_state.ghosts):
                ghost.x = float(ghost.home_x)
                ghost.y = float(ghost.home_y)
                ghost.is_edible = False
                ghost.xd = -1
                ghost.yd = -1
        # time.sleep(1)
