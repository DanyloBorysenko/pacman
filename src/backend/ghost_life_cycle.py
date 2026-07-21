"""Ghost edible/respawn timer bookkeeping."""
from ..state import GameState


class GhostLifecycleManager:
    """Manages timers, state changes, and edibility tracking for ghosts."""

    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def update_timers(self, dt: float) -> None:
        """Ticks down states for all ghosts regardless of
        whether they are moving."""
        for ghost in self.game_state.ghosts:
            if ghost.is_dead:
                ghost.time_since_death += dt
                if ghost.time_since_death >=\
                        self.game_state.config.ghost_reappear_time:
                    ghost.is_dead = False
                    ghost.time_since_death = 0
            elif ghost.is_edible:
                ghost.time_laps += dt
                if ghost.time_laps >= self.game_state.config.ghost_edible_time:
                    ghost.is_edible = False
                    ghost.time_laps = 0
                    ghost.colour = ghost.initial_colour
