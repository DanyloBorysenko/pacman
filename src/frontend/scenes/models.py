from enum import Enum


class MenuItem(Enum):
    """Available options displayed in the main menu."""
    START_GAME = "Start Game"
    VIEW_HIGHSCORES = "View Highscores"
    INSTRUCTIONS = "Instructions"
    EXIT = "Exit"


class PauseMenu(Enum):
    """Available options displayed in the pause menu."""
    CONTINUE = "Continue"
    MAIN_MENU = "Main menu"
