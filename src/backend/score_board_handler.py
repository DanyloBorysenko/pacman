import json
import os
from typing import List, Dict, Any


class ScoreBoardHandler:
<<<<<<< HEAD
    def __init__(self, path: str):
        self.file_path = path
        # Local cache array storing up to 10 player dict blocks: [{"name": "AAA", "score": 5000}]
        self.top_scores: List[Dict[str, Any]] = []
        # Automatically load existing history on instantiation
        self.load_top_players()

    def load_top_players(self) -> List[Dict[str, Any]]:
=======
    def __init__(self, path: str) -> None:
        self.file_path = path
        self.top_scores: List[Dict[str, Any]] = []
        self.load_top_players()

    def load_top_players(self) -> None:
>>>>>>> origin/backend_v0.2_refactor
        """
        Reads the JSON data file safely.
        If the file is absent or corrupted, initializes a clean,
        empty list profile structure.
        """
<<<<<<< HEAD
        self.player_list = []
        if not os.path.exists(self.file_path):
            self.top_scores = []
            return self.top_scores
=======
        self.player_list: List = []
        if not os.path.exists(self.file_path):
            self.top_scores = []
>>>>>>> origin/backend_v0.2_refactor

        try:
            with open(self.file_path, 'r') as file:
                self.top_scores = json.load(file)
        except (json.JSONDecodeError, IOError):
            self.top_scores = []

<<<<<<< HEAD
        return self.top_scores

    def get_player_list(self):
        if len(self.top_scores) > 0:
            return self.top_scores
        else:
            self.load_top_players()
        return self.player_list

    def is_in_top_scored(self, score: int) -> bool:
        """
        Determines if a newly finished game
        score qualifies for the leaderboard.
        Returns True if the board has room (< 10 entries)
        OR if it beats the lowest top score.
        """
        if len(self.top_scores) < 10:
            return True
        # Assumes list is kept sorted; last entry is the
        # lowest qualifying score
        return score > self.top_scores[-1]['score']

    def add_new_top_player(self, player_name: str, score: int) -> None:
=======
    def get_player_list(self) -> List[Dict[str, Any]]:
        if len(self.top_scores) == 0:
            self.load_top_players()
        return self.top_scores[:10] \
            if len(self.top_scores) > 10 else self.top_scores

    def add_new_player(self, player_name: str, score: int) -> None:
>>>>>>> origin/backend_v0.2_refactor
        """
        Appends the new record profile entry, sorts descending by score value,
        trims any entries past position 10, and updates the local storage file.
        """
        new_entry = {"name": player_name, "score": score}
        self.top_scores.append(new_entry)
<<<<<<< HEAD

        # Sort using Python lambda key descending by score
        self.top_scores.sort(key=lambda x: x['score'], reverse=True)

        # Slice array bounds strictly to keep top 10 elements
        self.top_scores = self.top_scores[:10]

        # Commit back to disk layout lines immediately
        self.save_to_file()

    def save_to_file(self) -> None:
        """Serializes the current in-memory leaderboard tracking list directly to the JSON target."""
=======
        self.top_scores.sort(key=lambda x: x['score'], reverse=True)
        # self.top_scores = self.top_scores
        self.save_to_file()

    def save_to_file(self) -> None:
        """Serializes the current in-memory leaderboard tracking
        list directly to the JSON target."""
>>>>>>> origin/backend_v0.2_refactor
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.top_scores, file, indent=4)
        except IOError as e:
<<<<<<< HEAD
            print(f"Error saving leaderboard data to disk matrix: {e}")
=======
            print(f"Error saving leaderboard data to disk matrix: {e}")
>>>>>>> origin/backend_v0.2_refactor
