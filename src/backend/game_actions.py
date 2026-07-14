"""Command-style rule actions applied to the game state."""
from abc import ABC, abstractmethod
from typing import Any
import numpy as np
from ..state import (
    GameState, BitMaps, VictoryEvent, Ghost,
    PacmanDiedEvent, Direction, GameOverEvent,
    GumEatenEvent, LevelUpEvent, CherryAppearedEvent,
    CherryEatenEvent
)


class GameAction(ABC):
    """Base class for a single, isolated rule change on the game state."""

    @abstractmethod
    def execute(self, state: GameState, **kwargs: Any) -> None:
        """Apply this action's rule change to the given state."""
        pass


class ConsumeItemsAction(GameAction):
    """Handles Pac-Man eating a pacgum, super pacgum, or cherry."""

    def execute(self, state: GameState, **kwargs: Any) -> None:
        """Award points/effects for whatever item is on Pac-Man's tile."""
        pacman = state.pacman

        y, x = int(pacman.y), int(pacman.x)
        current_tile = state.maze[y, x]

        if current_tile & BitMaps.PACGUM:
            state.live_status.current_score += state.config.points_per_pacgum
            state.maze[y, x] &= ~BitMaps.PACGUM
            state.packgum_collected += 1
            state.events.append(GumEatenEvent())
        elif current_tile & BitMaps.CHERRY:
            state.live_status.lives_remain += 1
            state.maze[y, x] &= ~BitMaps.CHERRY
            state.events.append(CherryEatenEvent())
        elif current_tile & BitMaps.SUPER_PACGUM:
            state.live_status.current_score += \
                state.config.points_per_super_pacgum
            state.maze[y, x] &= ~BitMaps.SUPER_PACGUM
            state.events.append(GumEatenEvent())
            for ghost in state.ghosts:
                if not ghost.is_dead:
                    ghost.is_edible = True
                    ghost.colour = "blue"
                    ghost.time_laps = 0

        if (state.packgum_collected >= state.config.pacgum // 2) and\
                not state.cherry_appeared:
            state.maze[state.pacman.start_y, state.pacman.start_x] |=\
                BitMaps.CHERRY
            state.cherry_appeared = True
            state.events.append(CherryAppearedEvent())


class CheckLevelClearAction(GameAction):
    """Detects when no pacgums remain and advances the level."""

    def execute(self, state: GameState, **kwargs: Any) -> None:
        """Trigger level advancement once all pacgums are eaten."""
        if np.any(state.maze & (BitMaps.SUPER_PACGUM | BitMaps.PACGUM)):
            return
        self.advance_to_next_level(state)

    def advance_to_next_level(self, state: GameState) -> None:
        """Move to the next level, or emit victory if at max_level."""
        if state.live_status.current_level == state.config.max_level:
            state.events.append(
                VictoryEvent(state.live_status.current_score))
        else:
            state.live_status.current_level += 1
            state.packgum_collected = 0
            state.cherry_appeared = False
            state.events.append(LevelUpEvent(state.live_status.current_level))
            state.live_status.pacman_curr_spd *= 1.10
            state.live_status.ghost_curr_speed *= 1.10

            from src.backend.game_initializer import GameInitializer
            initializer = GameInitializer(state)
            initializer.reload_new_level_map(state)

            state.pacman.xd = -1
            state.pacman.yd = -1
            state.pacman.assigned_direction = Direction.UP

        for ghost in state.ghosts:
            self._reset_ghost_state(ghost)

    def _reset_ghost_state(self, ghost: Ghost) -> None:
        """Return a ghost to its home tile with default state/colour."""
        ghost.x, ghost.y = float(ghost.home_x), float(ghost.home_y)
        ghost.xd, ghost.yd = -1, -1
        ghost.assigned_direction = (0, -1)
        ghost.is_edible = False
        ghost.is_dead = False
        ghost.time_laps = 0
        ghost.time_since_death = 0
        ghost.colour = ghost.initial_colour


class PlayerDeathAction(GameAction):
    """Handles Pac-Man losing a life: respawn, or game over."""

    def execute(self, state: GameState, **kwargs: Any) -> None:
        """Decrement lives and respawn, or emit game over if none remain."""
        state.live_status.lives_remain -= 1
        if state.live_status.lives_remain >= 0:
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
    """Handles Pac-Man eating a frightened ghost."""

    def execute(self, state: GameState, **kwargs: Any) -> None:
        """Award points and send the eaten ghost home to respawn."""
        ghost = kwargs.get("ghost")
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
