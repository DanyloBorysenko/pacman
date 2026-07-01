from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, TYPE_CHECKING, Tuple
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


@dataclass
class Pacman:
    # coord for the pacman center
    x: float
    y: float
    direction: Direction | None
    mouth_phase: float = 0.0
    xd: int = -1
    yd: int = -1
    assigned_direction: Direction | None = None
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
    paused: bool = True
    live_status: GameStats = None
    config: GameConfig = None

    # Cheat Mode flags
    create_invisibility: bool = False  #'I' 
    skip_level: bool = False  #'L'
