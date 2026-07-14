import os
import json
from typing import Dict, Any


def parse_game_config(file_path: str) -> Dict[str, Any]:
    """
    Parses configuration values from a JSON file.
    Supports comments starting with '#' and '//' by preprocessing the file.

    :param file_path: Path to the configuration JSON file.
    :return: A dictionary containing the parsed configurations.
    """
    # 1. Define default configurations as our baseline
    config_data: Dict[str, Any] = {
        "high_score_filename": "scoreboard.json",
        "maze_width": 15,
        "maze_height": 20,
        "lives": 3,
        "pacgum": 5,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "ghost_edible_time": 5.0,
        "ghost_reappear_time": 5.0,
        "seed": 42,
        "level_max_time": 60.0,
        "max_level": 2,
        "pacman_speed": 4.0,
        "ghost_speed": 3.2
    }

    if not os.path.exists(file_path):
        print(f"[Config Warning]: '{file_path}' not found. "
              "Using default internal settings.")
        return config_data

    try:
        clean_lines = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                clean_line = line.strip()

                if not clean_line or clean_line.startswith('#') or\
                        clean_line.startswith('//'):
                    continue

                clean_lines.append(clean_line)

        json_string = "".join(clean_lines)

        if not json_string:
            print("[Config Warning]: Configuration file is empty. "
                  "Using defaults.")
            return config_data

        parsed_json = json.loads(json_string)

        for key, value in parsed_json.items():
            if key in config_data:
                expected_type = type(config_data[key])

                try:
                    if expected_type is float and isinstance(
                            value, (int, float)):
                        config_data[key] = float(value)
                    elif isinstance(value, expected_type):
                        config_data[key] = value
                    else:
                        print(f"[Config Type Warning]: Key '{key}' "
                              f"expects type {expected_type.__name__}, "
                              f"but got {type(value).__name__}. "
                              "Retaining default.")
                except (ValueError, TypeError):
                    print(f"[Config Type Error]: Could not convert value "
                          f"'{value}' to key '{key}' "
                          f"expected type. Retaining default.")
            else:
                print(f"[Config Warning]: Unknown configuration key '{key}' "
                      "found in file. Skipping.")

    except json.JSONDecodeError as e:
        print(f"[Config Syntax Error]: Failed to parse JSON configuration"
              f"file. Details: {e}. Falling back to default settings.")
    except IOError as e:
        print(f"[Config Critical Error]: Failed to read file from disk. "
              f"Details: {e}. Falling back to default settings.")

    return config_data
