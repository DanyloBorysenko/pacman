from __future__ import annotations
from typing import List, TYPE_CHECKING, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum

if TYPE_CHECKING:
    from .backend.ghost_movement import GhostMovementStrategy


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


@dataclass
class GameConfig:
    high_score_filename: str = "scoreboard.json"
    lives: int = 3
    pacgum: int = 5
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    ghost_edible_time: float = 5.0
    seed: int = 42
    level_max_time: float = 60.0
    max_level: int = 1


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
    x: float = 0.0   # Floating point actual location
    y: float = 0.0
    xd: int = -1   # Int Target column destination
    yd: int = -1   # Int Target row destination
    assigned_direction: Direction = (0, 0)
    strategy: GhostMovementStrategy = None
    colour: str = None
    alpha: float = 1.0
    is_edible: bool = False
    edible_since: int | None = None
    time_laps: int = 0
    home_x: int = 0
    home_y: int = 0
    initial_colour: str = None


@dataclass
class GameStats:
    current_score: int = 0
    current_level: int = 1
    lives_remain: int = 3
    time_left: int = None
    is_edible: bool = False
    edible_time_left: int = 0


@dataclass
class GameState:
    maze: List[List[int]]
    pacman: Pacman
    ghosts: List[Ghost]
    live_status: GameStats = None
    config: GameConfig = None
    # Cheat Mode flags
    cheat_invincibility: bool = False  #'I'
    # 'L' for level skip
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


@dataclass
class LevelCompletedEvent(GameEvent):
    complited_level: int


@dataclass
class GameOverEvent(GameEvent):
    final_score: int


@dataclass
class VictoryEvent(GameEvent):
    final_score: int


@dataclass
class GameStartEvent(GameEvent):
    pass
