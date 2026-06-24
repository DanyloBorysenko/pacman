import pytest
import numpy as np
from src.backend.maze_renderer import generate_maze
from mazegenerator.mazegenerator import MazeGenerator

from src.backend.game_initializer import GameInitializer, WALL_MASK, PACGUM, SUPER_PACGUM, find_valid_center

class MockEntity:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

class MockConfig:
    def __init__(self):
        self.pacgum = 5  # Small, easy to verify count

class MockGameState:
    def __init__(self, maze_array: np.ndarray):
        self.maze = maze_array
        self.config = MockConfig()
        self.pacman = MockEntity()
        self.ghosts = [MockEntity() for _ in range(4)]


@pytest.fixture
def clean_maze_state():
    """Provides a completely open 5x5 maze for clean feature testing."""
    # An open 5x5 grid of 0s (no walls)
    # layout = np.zeros((5, 10), dtype=int)

    # original maze
    gen = MazeGenerator(size=(10, 15), seed=42)
    layout = np.array(gen.maze)
    return MockGameState(layout)


def test_exact_pacgum_count(clean_maze_state):
    """Verifies that exactly the number of gums requested in config are placed."""
    initializer = GameInitializer(clean_maze_state)
    initializer._place_pacgums()
    
    # Count how many elements have the PACGUM bit active
    gum_count = np.sum((clean_maze_state.maze & PACGUM) > 0)
    assert gum_count == clean_maze_state.config.pacgum
    generate_maze(initializer.game_state.maze)


def test_exclusions_in_gum_placement(clean_maze_state):
    """Ensures pacgums are never spawned on top of corners or the center tile."""
    initializer = GameInitializer(clean_maze_state)
    initializer._place_pacgums()
    
    # Check center tile
    cy, cx = initializer.valid_center
    assert (clean_maze_state.maze[cy, cx] & PACGUM) == 0
    
    # Check all corners
    for cy, cx in initializer.corners:
        assert (clean_maze_state.maze[cy, cx] & PACGUM) == 0
    generate_maze(initializer.game_state.maze)


def test_super_pacgum_placement(clean_maze_state):
    """Verifies super gums populate the 4 corners and clear any existing regular gums."""
    initializer = GameInitializer(clean_maze_state)
    
    # Force add regular gums to the corners manually to test cleansing logic
    for y, x in initializer.corners:
        clean_maze_state.maze[y, x] |= PACGUM
        
    initializer._place_super_pacgums()
    
    for y, x in initializer.corners:
        # Regular gum must be wiped out
        assert (clean_maze_state.maze[y, x] & PACGUM) == 0
        # Super gum bit must be active
        assert (clean_maze_state.maze[y, x] & SUPER_PACGUM) > 0
    generate_maze(initializer.game_state.maze)


def test_center_blocked_fallback():
    """Tests that find_valid_center finds an open tile if the true center is a solid wall."""
    # Create a 5x5 grid where the center (2, 2) is a solid block (15)
    # but (2, 1) is a completely open corridor (0)
    blocked_layout = np.zeros((5, 5), dtype=int)
    blocked_layout[2, 2] = 15 
    
    valid_y, valid_x = find_valid_center(blocked_layout)
    
    # It must not choose the blocked tile
    assert (valid_y, valid_x) != (2, 2)
    # It should find the nearest available corridor piece
    assert (blocked_layout[valid_y, valid_x] & WALL_MASK) < 15