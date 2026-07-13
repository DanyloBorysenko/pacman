import json
import os
from typing import List, Dict, Any


class ScoreBoardHandler:
    def __init__(self, path: str) -> None:
        self.file_path = path
        self.top_scores: List[Dict[str, Any]] = []
        self.load_top_players()

    def load_top_players(self) -> None:
        """
        Reads the JSON data file safely.
        If the file is absent or corrupted, initializes a clean,
        empty list profile structure.
        """
        self.player_list: List = []
        if not os.path.exists(self.file_path):
            self.top_scores = []

        try:
            with open(self.file_path, 'r') as file:
                self.top_scores = json.load(file)
        except (json.JSONDecodeError, IOError):
            self.top_scores = []

    def get_player_list(self, top_ten: bool) -> List[Dict[str, Any]]:
        if len(self.top_scores) == 0:
            self.load_top_players()
        return self.top_scores[:10] \
            if top_ten else self.top_scores

    def add_new_player(self, player_name: str, score: int) -> bool:
        """
        Validates player name (max 10 chars, alphanumeric/spaces only).
        If valid, appends the entry, sorts, saves, and returns True.
        If invalid, returns False.
        """
        if len(player_name) > 10:
            return False
        if not player_name.replace(" ", "").isalnum():
            return False
        new_entry = {"name": player_name, "score": score}
        self.top_scores.append(new_entry)
        self.top_scores.sort(key=lambda x: x['score'], reverse=True)
        # self.top_scores = self.top_scores
        self.save_to_file()
        return True

    def save_to_file(self) -> None:
        """Serializes the current in-memory leaderboard tracking
        list directly to the JSON target."""
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.top_scores, file, indent=4)
        except IOError as e:
            print(f"Error saving leaderboard data to disk matrix: {e}")
