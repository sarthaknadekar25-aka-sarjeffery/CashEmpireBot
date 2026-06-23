import os
import json
import threading

DATA_FILE = "data/economy.json"

_db_lock = threading.Lock()
_db_conn = None
_db_ready = False

DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    import psycopg2
    import psycopg2.extras

    _db_conn = psycopg2.connect(DATABASE_URL)
    _db_conn.autocommit = True
    cur = _db_conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            uid TEXT PRIMARY KEY,
            data JSONB NOT NULL DEFAULT '{}'
        )
    """)
    cur.close()
    _db_ready = True


def load_data():
    if _db_ready:
        with _db_lock:
            cur = _db_conn.cursor()
            cur.execute("SELECT uid, data FROM players")
            rows = cur.fetchall()
            cur.close()
            return {row[0]: dict(row[1]) for row in rows}
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_data(data):
    if _db_ready:
        with _db_lock:
            cur = _db_conn.cursor()
            cur.execute("DELETE FROM players")
            if data:
                psycopg2.extras.execute_values(
                    cur,
                    "INSERT INTO players (uid, data) VALUES %s",
                    [(uid, json.dumps(pd)) for uid, pd in data.items()]
                )
            cur.close()
        return
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


DEFAULT_PLAYER = {
    "balance": 100, "last_daily": None,
    "multiplier_2x_expires": None, "multiplier_5x_expires": None,
    "pets": [], "inventory": {}, "luck_boost": 0,
    "xp": 0, "messages": 0, "commands": 0
}


def get_player(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = dict(DEFAULT_PLAYER)
    return data[uid]


def migrate_pets(player):
    new_pets = []
    for pet in player.get("pets", []):
        if isinstance(pet, str):
            mapping = {"dog": ("Pet Dog", "🐾", "Common", 1.2), "cat": ("Pet Cat", "🐾", "Uncommon", 1.5), "dragon": ("Pet Dragon", "🐾", "Rare", 2.0)}
            name, emoji, rarity, mult = mapping.get(pet, (pet.capitalize(), "🐾", "Common", 1.2))
            new_pets.append({"name": name, "emoji": emoji, "rarity": rarity, "multiplier": mult, "active": len(new_pets) == 0, "crate": "legacy"})
        else:
            new_pets.append(pet)
    player["pets"] = new_pets
