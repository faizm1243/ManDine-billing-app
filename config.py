import json
import os

CONFIG_FILE = "mandine_config.json"

DEFAULT_DB_PATH = r"\\MANDINE-NAS\mandine_data\mandine.db"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_db_path():
    config = load_config()
    return config.get("db_path", DEFAULT_DB_PATH)

def set_db_path(path):
    config = load_config()
    config["db_path"] = path
    save_config(config)
