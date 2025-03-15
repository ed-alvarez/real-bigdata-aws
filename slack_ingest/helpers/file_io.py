import json
import os


def ensure_dir(path: str):
    # Ensure local dir exists
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def save_data_to_path(data, path: str) -> bool:
    ensure_dir(path)
    with open(path, "w+") as f:
        json.dump(data, f, indent=True)

    return True
