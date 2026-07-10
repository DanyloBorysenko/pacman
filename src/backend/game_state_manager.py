import math
import numpy as np
from ..state import (
    GameState, Direction, BitMaps, Ghost,
    GameOverEvent, GhostEatenEvent,
    PacmanDiedEvent, VictoryEvent
    )
from .game_motion import PacmanMovementController, GhostMovementController
from .ghost_life_cycle import GhostLifecycleManager
from .game_actions import ConsumeItemsAction, CheckLevelClearAction


class GameStateManager:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.pacman_ctrl = PacmanMovementController(game_state)
        self.ghost_ctrl = GhostMovementController(game_state)
        self.ghost_lifecycle = GhostLifecycleManager(game_state)

        # Register our modular rule pieces into an execution pipeline!
        self.arrival_actions = [
            ConsumeItemsAction(),
            CheckLevelClearAction(advancer_callback=self._advance_to_next_level)
        ]

    def update_remaining_time(self, dt: float) -> None:
        # if self.game_state.paused:
        #     return

        self.game_state.live_status.time_left -= dt
        if self.game_state.live_status.time_left <= 0:
            # print("Time's up")
            self._process_player_death()
            self.game_state.live_status.time_left =\
                self.game_state.config.level_max_time

    def update_pacman(self, dt: float, requested_direction: Direction) -> None:
        """The central heartbeat tick. Pass dt here from
        your main clock loop."""
        # 1. Ask the movement sub-controller to shift coordinates
        arrived, _ = self.pacman_ctrl.update(dt, requested_direction)
        
        # 2. If he safely landed on a new tile, just run the pipeline pieces
        if arrived:
            for action in self.arrival_actions:
                action.execute(self.game_state)

    def _advance_to_next_level(self) -> None:
        """Handles state resets and difficulty scaling
        when a level is cleared."""
        state = self.game_state
        if state.live_status.current_level == state.config.max_level:
            state.events.append(
                VictoryEvent(state.live_status.current_score))
            # print("Victory is achived")
        else:
            state.live_status.current_level += 1
            self.game_state.live_status.pacman_curr_spd *= 1.10
            self.game_state.live_status.ghost_curr_speed *= 1.10

            # 3. Request a fresh maze matrix from your generator
            from src.backend.game_initializer import GameInitializer
            initializer = GameInitializer(state)
            initializer.reload_new_level_map(self.game_state)

            # 4. Reset Pac-Man physics markers completely
            state.pacman.xd = -1
            state.pacman.yd = -1
            state.pacman.assigned_direction = self.game_state.pacman.direction

        # 5. Reset all Ghosts physics and state trackers completely
        for ghost in state.ghosts:
            self._reset_ghost_state(ghost)

    def _reset_ghost_state(self, ghost: Ghost) -> None:
        ghost.x, ghost.y = float(ghost.home_x), float(ghost.home_y)
        ghost.xd, ghost.yd = -1, -1
        ghost.assigned_direction = (0, -1)
        ghost.is_edible = False
        ghost.is_dead = False
        ghost.time_laps = 0
        ghost.time_since_death = 0
        ghost.colour = ghost.initial_colour

    def set_ghost_edible_time_laps(self, ghost: Ghost, dt: float) -> None:
        # print(f"Ghost edible, time laps: {ghost.time_laps}")
        ghost.time_laps += dt
        if ghost.time_laps >= self.game_state.config.ghost_edible_time:
            ghost.is_edible = False
            ghost.time_laps = 0
            ghost.colour = ghost.initial_colour

    def set_ghost_reappearance_time_laps(
            self, ghost: Ghost, dt: float) -> None:
        # print(f"Ghost edible, time laps: {ghost.time_laps}")
        ghost.time_since_death += dt
        if ghost.time_since_death >=\
                self.game_state.config.ghost_reappear_time:
            print(f"{ghost.colour} reappeared after "
                  f"{ghost.time_since_death} s at x: {ghost.x}, y: {ghost.y}")
            ghost.is_dead = False
            ghost.time_since_death = 0

    def update_ghosts(self, dt: float) -> None:
        """Updates all ghosts using fractional time slices and
        coordinates their AI changes."""
        # 1. Tick status timers down (edibility, respawn)
        self.ghost_lifecycle.update_timers(dt)
        # 2. Move ghosts
        self.ghost_ctrl.update(dt)

    def check_collisions(self) -> None:
        """Evaluates proximity between Pac-Man and all ghosts,
        triggering state updates."""
        pacman = self.game_state.pacman

        for ghost in self.game_state.ghosts:
            if ghost.is_dead:
                continue

            distance = math.sqrt(
                (pacman.x - ghost.x)**2 + (pacman.y - ghost.y)**2)

            if distance < 0.5:
                if ghost.is_edible:
                    # print(f"ghost is eaten, time laps: {ghost.time_laps}")
                    self._process_ghost_eaten(ghost)
                else:
                    if self.game_state.cheat_invincibility:
                        continue
                    self._process_player_death()
                    break

    def _process_ghost_eaten(self, ghost: Ghost) -> None:
        """Handles Step B: Pac-Man devours an edible ghost."""
        # 1. Award points dynamically from config
        self.game_state.live_status.current_score +=\
            self.game_state.config.points_per_ghost
        self.game_state.events.append(
            GhostEatenEvent(ghost, (ghost.x, ghost.y)))

        # 2. Reset this specific ghost's state flags
        ghost.is_edible = False
        ghost.is_dead = True
        ghost.time_laps = 0
        ghost.time_since_death = 0
        ghost.colour = ghost.initial_colour

        # 3. Teleport the ghost back to its starting coordinate layout
        # (Assuming your state handles individual home corners)
        ghost.x = float(ghost.home_x)
        ghost.y = float(ghost.home_y)

        # 4. Reset its GridMover targets so it doesn't try to
        # glide back outwards sideways
        ghost.xd = -1
        ghost.yd = -1
        # time.sleep(1)

    def _process_player_death(self) -> None:
        """Handles Step A: Player loses a life to a dangerous ghost."""
        # 1. Deduct life status
        self.game_state.live_status.lives_remain -= 1
        if self.game_state.live_status.lives_remain > 0:
            death_coord = (self.game_state.pacman.x, self.game_state.pacman.y)
            self.game_state.events.append(
                PacmanDiedEvent(self.game_state.pacman, death_coord))
        print(f"live remains: {self.game_state.live_status.lives_remain}")

        # 2. Check for game over state transition
        if self.game_state.live_status.lives_remain <= 0:
            # self.game_state.current_screen = "GAME_OVER"
            self.game_state.events.append(
                GameOverEvent(self.game_state.live_status.current_score))
            # self.game_state.paused = True
        else:
            # 3. Respawn Pac-Man at the map's safe starting center
            self.game_state.pacman.x = float(self.game_state.pacman.start_x)
            self.game_state.pacman.y = float(self.game_state.pacman.start_y)

            # 4. Clear Pac-Man's GridMover destination states
            self.game_state.pacman.xd = -1
            self.game_state.pacman.yd = -1
            self.game_state.pacman.assigned_direction = Direction.UP

            # 5. Optional Peer Tip: Reset all ghosts to their homes on death
            # to prevent instant spawn-killing when Pac-Man reappears!
            for i, ghost in enumerate(self.game_state.ghosts):
                ghost.x = float(ghost.home_x)
                ghost.y = float(ghost.home_y)
                ghost.is_edible = False
                ghost.xd = -1
                ghost.yd = -1
        # time.sleep(1)
