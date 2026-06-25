from typing import Tuple
from ..state import GameState, Direction, BitMaps

PACMAN_SPEED = 0.1
GHOST_SPEED = 0.1


class GameStateManager:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def request_move(self, direction: Direction) -> None:
        curr_x = int(self.game_state.pacman.x)
        curr_y = int(self.game_state.pacman.y)
        curr_tile = self.game_state.maze[curr_y, curr_x]
        # self.game_state.pacman.direction = direction
        print(f"Pacman: {self.game_state.pacman.x}, {self.game_state.pacman.y}")
        if (abs(curr_x - self.game_state.pacman.x) <= 0.01) and\
            (abs(curr_y - self.game_state.pacman.y) <= 0.01):
            if self._is_move_allowed(curr_tile, direction):
                self.move(curr_tile, curr_x, curr_y)
        else:
            self.game_state.pacman.x += direction.value[0] * PACMAN_SPEED
            self.game_state.pacman.y += direction.value[1] * PACMAN_SPEED

    def _is_move_allowed(self, curr_tile: int, direction: Direction) -> bool:
        if direction == Direction.RIGHT and (curr_tile & BitMaps.EAST):
            return False
        elif direction == Direction.LEFT and (curr_tile & BitMaps.WEST):
            return False
        elif direction == Direction.UP and (curr_tile & BitMaps.NORTH):
            return False
        elif direction == Direction.DOWN and (curr_tile & BitMaps.SOUTH):
            return False
        return True

    def move(self, current_tile: int, x: int, y: int) -> None:
        # new_x = int(self.game_state.pacman.x)
        # new_y = int(self.game_state.pacman.y)
        # print(f"later: {new_x}, {new_y}")
        # new_tile = self.game_state.maze[new_y, new_x]

        if (current_tile & BitMaps.PACGUM):
            self.game_state.live_status.current_score += self.game_state.config.points_per_pacgum.value
            self.game_state.maze[y, x] &= ~BitMaps.PACGUM
        elif (current_tile & BitMaps.SUPER_PACGUM):
            self.game_state.live_status.current_score += self.game_state.config.points_per_super_pacgum.v
            self.game_state.maze[y, x] &= ~BitMaps.SUPER_PACGUM
            pass
