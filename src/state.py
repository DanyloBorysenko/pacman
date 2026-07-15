from __future__ import annotations
from typing import List, TYPE_CHECKING, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import numpy as np

if TYPE_CHECKING:
    from .backend.ghost_movement_logic import GhostMovementStrategy


class GameAudioFile(Enum):
    """Maps game audio cues to their asset file paths."""
    BACKGROUND = "assets/audio/pacmans-start.ogg"
    INTRO = "assets/audio/pacman_ringtone.ogg"
    PACMAN_MUNCH = "assets/audio/wakka.ogg"
    GHOST_EATING = "assets/audio/ghost-eaten.ogg"
    FRUIT_EATING = "assets/audio/pacman_eatfruit.ogg"
    GHOST_CHASING = "assets/audio/siren.ogg"
    GHOST_FLEEING = "assets/audio/ghost-retreat.ogg"
    DEATH = "assets/audio/pacman_death.ogg"


class Direction(Enum):
    """Cardinal movement directions, each stored as an (dx, dy)
    unit-vector tuple."""

    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    UP = (0, -1)


class BitMaps(IntEnum):
    """Bit flags packed into a single maze cell integer.

    NORTH/SOUTH/EAST/WEST mark which walls a cell has, WALL_MASK
    covers all four wall bits, and PACGUM/SUPER_PACGUM/CHERRY are
    collectible flags combinable with wall bits via bitwise OR.
    """

    NORTH = 1
    SOUTH = 4
    WEST = 8
    EAST = 2
    WALL_MASK = 15
    PACGUM = 16
    SUPER_PACGUM = 32
    CHERRY = 64


@dataclass
class GameConfig:
    """Tunable game parameters loaded once per run/level, covering
    maze size, scoring, timers, and entity speeds."""

    high_score_filename: str = "scoreboard.json"
    maze_width: int = 15
    maze_height: int = 20
    lives: int = 3
    pacgum: int = 5
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    ghost_edible_time: float = 5.0
    ghost_reappear_time: float = 5.0
    seed: int = 42
    level_max_time: float = 60.0
    max_level: int = 10
    pacman_speed: float = 4.0
    ghost_speed: float = 3.2


@dataclass
class Pacman:
    """Player entity state.

    x/y are the center coordinate of Pacman. direction is the
    current facing/movement direction, while assigned_direction
    tracks the queued turn used for cornering logic.
    """

    # coord for the pacman center
    x: float
    y: float
    direction: Direction = Direction.UP
    mouth_phase: float = 0.0
    death_phase: float = 0.0
    xd: int = -1
    yd: int = -1
    assigned_direction: Direction = Direction.UP
    start_x: int = 0
    start_y: int = 0


@dataclass
class Ghost:
    """Ghost entity state.

    colour/initial_colour distinguish the current display color from
    the original one, used when toggling edible state. home_x/home_y
    is the respawn point after being eaten.
    """

    x: float = 0.0
    y: float = 0.0
    xd: int = -1
    yd: int = -1
    assigned_direction: Tuple[int, int] = (0, 0)
    strategy: GhostMovementStrategy | None = None
    colour: str | None = None
    alpha: float = 1.0
    is_edible: bool = False
    time_laps: float = 0.0
    is_dead: bool = False
    time_since_death: float = 0.0
    home_x: int = 0
    home_y: int = 0
    initial_colour: str | None = None


@dataclass
class GameStats:
    """Live HUD data: score, level, lives, remaining time, and
    current edibility/speed status for display."""

    current_score: int = 0
    current_level: int = 1
    lives_remain: int = 3
    time_left: float = 90.0
    is_edible: bool = False
    edible_time_left: int = 0
    pacman_curr_spd: float = 0
    ghost_curr_speed: float = 0


@dataclass
class GameState:
    """Aggregate root holding the full game snapshot for a frame.

    events collects GameEvent instances produced this frame (e.g.
    a gum eaten, a ghost death); consumers such as audio, scoring,
    and UI transitions drain and react to them each update.
    """

    maze: np.ndarray
    pacman: Pacman
    ghosts: List[Ghost]
    live_status: GameStats
    config: GameConfig
    packgum_collected: int = 0
    cherry_appeared: bool = False
    # Cheat Mode flags
    cheat_invincibility: bool = False
    cheat_freeze: bool = False
    events: List["GameEvent"] = field(default_factory=list)


@dataclass
class GameEvent:
    """Base class for all game events dispatched via
    GameState.events."""
    pass


@dataclass
class PacmanDiedEvent(GameEvent):
    """Fired when Pacman is caught by a ghost."""
    pacman: Pacman
    death_coord: Tuple[float, float]


@dataclass
class GhostEatenEvent(GameEvent):
    """Fired when Pacman eats an edible ghost."""
    ghost: Ghost
    death_coord: Tuple[float, float]


@dataclass
class LevelUpEvent(GameEvent):
    """Fired when the player clears a level and advances."""
    next_level: int


@dataclass
class GameOverEvent(GameEvent):
    """Fired when the player runs out of lives."""
    final_score: int


@dataclass
class VictoryEvent(GameEvent):
    """Fired when the player clears the final level."""
    final_score: int


@dataclass
class GameStartEvent(GameEvent):
    """Fired when a new game run begins."""
    pass


@dataclass
class GumEatenEvent(GameEvent):
    """Fired when Pacman eats a pacgum or super pacgum."""
    pass


@dataclass
class CherryAppearedEvent(GameEvent):
    """Fired when a bonus cherry spawns in the maze."""
    pass


@dataclass
class CherryEatenEvent(GameEvent):
    """Fired when Pacman eats the bonus cherry."""
    pass
