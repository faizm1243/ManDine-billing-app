import json
import os
import sqlite3

CONFIG_FILE = "mandine_config.json"

# Default NAS path
DEFAULT_DB_PATH = r"\\MANDINE-NAS\mandine_data\mandine.db"

# Local fallback path (always works)
LOCAL_DB_PATH = os.path.join(os.getcwd(), "mandine_local.db")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def can_open_db(path):
    try:
        conn = sqlite3.connect(path)
        conn.close()
        return True
    except Exception:
        return False


def get_db_path():
    config = load_config()
    configured_path = config.get("db_path")

    # 1️⃣ If admin configured a path, try it
    if configured_path and can_open_db(configured_path):
        return configured_path

    # 2️⃣ Try default NAS
    if can_open_db(DEFAULT_DB_PATH):
        return DEFAULT_DB_PATH

    # 3️⃣ Fallback to local DB (guaranteed)
    return LOCAL_DB_PATH


def set_db_path(path):
    config = load_config()
    config["db_path"] = path
    save_config(config)
