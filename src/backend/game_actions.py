from abc import ABC, abstractmethod
import numpy as np
from ..state import (
    GameState, BitMaps, VictoryEvent, Ghost,
    PacmanDiedEvent, Direction, GameOverEvent
)


class GameAction(ABC):
    @abstractmethod
    def execute(self, state: GameState, **kwargs) -> None:
        """Process a isolated rule change on the game state."""
        pass


class ConsumeItemsAction(GameAction):
    def execute(self, state: GameState, **kwargs) -> None:
        pacman = state.pacman

        y, x = int(pacman.y), int(pacman.x)
        current_tile = state.maze[y, x]

        if current_tile & BitMaps.PACGUM:
            state.live_status.current_score += state.config.points_per_pacgum
            state.maze[y, x] &= ~BitMaps.PACGUM
        elif current_tile & BitMaps.SUPER_PACGUM:
            state.live_status.current_score += \
                state.config.points_per_super_pacgum
            state.maze[y, x] &= ~BitMaps.SUPER_PACGUM
            for ghost in state.ghosts:
                ghost.is_edible = True
                ghost.colour = "blue"
                ghost.time_laps = 0


class CheckLevelClearAction(GameAction):
    def execute(self, state: GameState, **kwargs) -> None:
        if np.any(state.maze & (BitMaps.SUPER_PACGUM | BitMaps.PACGUM)):
            return
        self.advance_to_next_level(state)

    def advance_to_next_level(self, state: GameState) -> None:
        if state.live_status.current_level == state.config.max_level:
            state.events.append(
                VictoryEvent(state.live_status.current_score))
        else:
            state.live_status.current_level += 1
            state.live_status.pacman_curr_spd *= 1.10
            state.live_status.ghost_curr_speed *= 1.10

            from src.backend.game_initializer import GameInitializer
            initializer = GameInitializer(state)
            initializer.reload_new_level_map(state)

            state.pacman.xd = -1
            state.pacman.yd = -1
            state.pacman.assigned_direction = state

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


class PlayerDeathAction(GameAction):
    def execute(self, state: GameState, **kwargs) -> None:
        state.live_status.lives_remain -= 1
        if state.live_status.lives_remain > 0:
            death_coord = (state.pacman.x, state.pacman.y)
            state.events.append(
                PacmanDiedEvent(state.pacman, death_coord))
        if state.live_status.lives_remain <= 0:
            state.events.append(
                GameOverEvent(state.live_status.current_score))
        else:
            state.pacman.x = float(state.pacman.start_x)
            state.pacman.y = float(state.pacman.start_y)

            state.pacman.xd = -1
            state.pacman.yd = -1
            state.pacman.assigned_direction = Direction.UP

            for i, ghost in enumerate(state.ghosts):
                ghost.x, ghost.y = float(ghost.home_x), float(ghost.home_y)
                ghost.xd, ghost.yd = -1, -1
                ghost.assigned_direction = (0, -1)
                ghost.is_edible = False
                ghost.is_dead = False
                ghost.time_laps = 0
                ghost.time_since_death = 0
                ghost.colour = ghost.initial_colour


class GhostEatenAction(GameAction):
    def execute(self, state: GameState, **kwargs) -> None:
        ghost: Ghost = kwargs.get("ghost")
        if not ghost:
            return

        from ..state import GhostEatenEvent

        state.live_status.current_score += state.config.points_per_ghost
        state.events.append(GhostEatenEvent(ghost, (ghost.x, ghost.y)))

        ghost.is_edible = False
        ghost.is_dead = True
        ghost.time_laps = 0
        ghost.time_since_death = 0
        ghost.colour = ghost.initial_colour

        ghost.x, ghost.y = float(ghost.home_x), float(ghost.home_y)
        ghost.xd, ghost.yd = -1, -1
