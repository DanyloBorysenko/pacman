import os
from typing import Dict, Any


def parse_game_config(file_path: str) -> Dict[str, Any]:
    """
    Parses configuration values from a plaintext file, skipping lines starting with '#'.

    :param file_path: Path to the configuration text file.
    :return: A dictionary containing the parsed configurations.
    """
    # Define default configurations as our baseline
    config_data: Dict[str, Any] = {
        "high_score_filename": "scoreboard.json",
        "maze_width": 10,
        "maze_height": 15,
        "lives": 3,
        "pacgum": 5,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "ghost_edible_time": 5.0,
        "seed": 42,
        "level_max_time": 60.0,
        "max_level": 2,
        "pacman_speed": 4.0,
        "ghost_speed": 3.2
    }

    if not os.path.exists(file_path):
        print(f"[Config Warning]: '{file_path}' not found. Using default internal settings.")
        return config_data

    try:
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, 1):
                clean_line = line.strip()
                
                # Skip completely empty lines or comment lines starting with '#'
                if not clean_line or clean_line.startswith('#'):
                    continue
                
                # Ensure the line follows a clear key=value structure
                if '=' not in clean_line:
                    print(f"[Config Syntax Error] Line {line_num}: Missing '=' delimiter. Skipping line.")
                    continue
                
                key, val = clean_line.split('=', 1)
                key = key.strip()
                val = val.strip()
                
                if key not in config_data:
                    print(f"[Config Warning] Line {line_num}: Unknown configuration key '{key}'. Skipping.")
                    continue
                
                # Validate and cast types carefully depending on what the key expects
                try:
                    if key == "high_score_filename":
                        config_data[key] = val
                    elif key in ["ghost_edible_time",
                                 "level_max_time",
                                 "pacman_speed",
                                 "ghost_speed"]:
                        config_data[key] = float(val)
                    else:
                        config_data[key] = int(val)
                except ValueError:
                    print(f"[Config Type Error] Line {line_num}: Invalid value '{val}' for key '{key}'. Retaining default.")
               
    except IOError as e:
        print(f"[Config Critical Error]: Failed to read file from disk. Details: {e}")

    return config_data
