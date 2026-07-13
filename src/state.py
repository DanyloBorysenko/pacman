from __future__ import annotations
from typing import List, TYPE_CHECKING, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import numpy as np

if TYPE_CHECKING:
    from .backend.ghost_movement_logic import GhostMovementStrategy


class GameAudioFile(Enum):
    BACKGROUND = "assets/audio/pacmans-start.ogg"
    INTRO = "assets/audio/pacman_ringtone.ogg"
    PACMAN_MUNCH = "assets/audio/wakka.ogg"
    GHOST_EATING = "assets/audio/ghost-eaten.ogg"
    FRUIT_EATING = "assets/audio/pacman_eatfruit.ogg"
    GHOST_CHASING = "assets/audio/siren.ogg"
    GHOST_FLEEING = "assets/audio/ghost-retreat.ogg"
    DEATH = "assets/audio/pacman_death.ogg"


class Direction(Enum):
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    UP = (0, -1)


class BitMaps(IntEnum):
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
    """Base class for all game events."""
    pass


@dataclass
class PacmanDiedEvent(GameEvent):
    pacman: Pacman
    death_coord: Tuple[float, float]


@dataclass
class GhostEatenEvent(GameEvent):
    ghost: Ghost
    death_coord: Tuple[float, float]


@dataclass
class LevelUpEvent(GameEvent):
    next_level: int


@dataclass
class GameOverEvent(GameEvent):
    final_score: int


@dataclass
class VictoryEvent(GameEvent):
    final_score: int


@dataclass
class GameStartEvent(GameEvent):
    pass


@dataclass
class GumEatenEvent(GameEvent):
    pass


@dataclass
class CherryAppearedEvent(GameEvent):
    pass


@dataclass
class CherryEatenEvent(GameEvent):
    pass
