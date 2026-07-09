import json
import os
from typing import List, Dict, Any


class ScoreBoardHandler:
    def __init__(self, path: str) -> None:
        self.file_path = path
        # Local cache array storing up to 10 player dict blocks:
        # [{"name": "AAA", "score": 5000}]
        self.top_scores: List[Dict[str, Any]] = []
        # Automatically load existing history on instantiation
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

    def get_player_list(self) -> List[Dict[str, Any]]:
        if len(self.top_scores) == 0:
            self.load_top_players()
        return self.top_scores[:10] \
            if len(self.top_scores) > 10 else self.top_scores

    # def is_in_top_scored(self, score: int) -> bool:
    #     """
    #     Determines if a newly finished game
    #     score qualifies for the leaderboard.
    #     Returns True if the board has room (< 10 entries)
    #     OR if it beats the lowest top score.
    #     """
    #     if len(self.top_scores) < 10:
    #         return True
    #     return score > self.top_scores[-1]['score']

    def add_new_player(self, player_name: str, score: int) -> None:
        """
        Appends the new record profile entry, sorts descending by score value,
        trims any entries past position 10, and updates the local storage file.
        """
        new_entry = {"name": player_name, "score": score}
        self.top_scores.append(new_entry)
        self.top_scores.sort(key=lambda x: x['score'], reverse=True)
        # self.top_scores = self.top_scores
        self.save_to_file()

    def save_to_file(self) -> None:
        """Serializes the current in-memory leaderboard tracking
        list directly to the JSON target."""
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.top_scores, file, indent=4)
        except IOError as e:
            print(f"Error saving leaderboard data to disk matrix: {e}")
