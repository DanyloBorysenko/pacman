"""Per-frame orchestrator that advances the game simulation."""
from ..state import GameState, Direction
from .game_physics import PacmanMovementController, GhostMovementController
from .ghost_life_cycle import GhostLifecycleManager
from .game_actions import (
    ConsumeItemsAction, CheckLevelClearAction,
    GhostEatenAction, PlayerDeathAction
)


class GameStateManager:
    """Composes movement controllers, timers, and actions into one
    per-frame update pipeline."""

    def __init__(self, game_state: GameState):
        """Wire up the movement/lifecycle controllers and game actions."""
        self.game_state = game_state
        self.pacman_ctrl = PacmanMovementController(game_state)
        self.ghost_ctrl = GhostMovementController(game_state)
        self.ghost_lifecycle = GhostLifecycleManager(game_state)

        # Game Actions
        self.consume_item_action = ConsumeItemsAction()
        self.level_clearance_action = CheckLevelClearAction()
        self.ghost_eaten_action = GhostEatenAction()
        self.player_death_action = PlayerDeathAction()

    def update_remaining_time(self, dt: float) -> None:
        """Tick the level clock down, costing a life if it runs out."""
        self.game_state.live_status.time_left -= dt
        if self.game_state.live_status.time_left <= 0:
            self.player_death_action.execute(self.game_state)
            self.game_state.live_status.time_left =\
                self.game_state.config.level_max_time

    def update_pacman(self, dt: float, requested_direction: Direction) -> None:
        """The central heartbeat tick. Pass dt here from
        your main clock loop."""
        # 1. Ask the movement sub-controller to shift coordinates
        arrived, _ = self.pacman_ctrl.update(dt, requested_direction)

        # 2. If he safely landed on a new tile, just run the pipeline pieces
        if arrived:
            self.consume_item_action.execute(self.game_state)
            self.level_clearance_action.execute(self.game_state)

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
            distance = (pacman.x - ghost.x)**2 + (pacman.y - ghost.y)**2
            if distance < 0.25:
                if ghost.is_edible:
                    self.ghost_eaten_action.execute(
                        self.game_state, ghost=ghost)
                else:
                    if self.game_state.cheat_invincibility:
                        continue
                    self.player_death_action.execute(self.game_state)
                    break
