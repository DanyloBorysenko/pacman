from dataclasses import dataclass, field
from typing import List
from enum import Enum, IntEnum


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


class GameConfig(Enum):
    high_score_filename = None
    lives = 3
    pacgum = 42
    points_per_pacgum = 10
    points_per_super_pacgum = 50
    points_per_ghost = 200
    seed = 42
    level_max_time = 90


class CheatModes(Enum):
    pass


@dataclass
class Pacman:
    # coord for the pacman center
    x: float
    y: float
    direction: Direction | None
    mouth_phase: float = 0.0
    death_phase: float = 0.0
    xd: int = -1
    yd: int = -1
    assigned_direction: Direction | None = None


@dataclass
class Ghost:
    # coordinate for ghost
    x: float
    y: float
    assigned_direction: Direction
    is_edibe: bool = False
    edible_since: int | None = None
    colour: str = None


@dataclass
class GameStats:
    current_score: int = 0
    current_level: int = 1
    lives_remain: int = 3
    time_left: int = 100
    cheat_mode: bool = False


@dataclass
class GameState:
    maze: List[List[int]]
    pacman: Pacman
    ghosts: List[Ghost]
    live_status: GameStats = None
    config: GameConfig = None
    events: List["GameEvent"] = field(default_factory=list)


@dataclass
class GameEvent:
    """Base class for all game events."""
    pass


@dataclass
class PacmanDiedEvent(GameEvent):
    pacman: Pacman


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
