import os
import json

_db_ready = False
_db_conn = None

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NEON_DB_URL") or ""
if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    try:
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
        print("[DB] PostgreSQL connected!", flush=True)
    except Exception as e:
        _db_ready = False
        print(f"[DB] PostgreSQL connection FAILED: {e}", flush=True)
else:
    print(f"[DB] DATABASE_URL not set or not PostgreSQL", flush=True)

JSON_FILE = "data/economy.json"


def load_data():
    if _db_ready:
        try:
            cur = _db_conn.cursor()
            cur.execute("SELECT uid, data FROM players")
            rows = cur.fetchall()
            cur.close()
            if rows:
                return {row[0]: dict(row[1]) for row in rows}
        except Exception as e:
            print(f"[DB] load_data query failed: {e}", flush=True)
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE) as f:
            data = json.load(f)
        if data and _db_ready:
            try:
                cur = _db_conn.cursor()
                cur.execute("DELETE FROM players")
                psycopg2.extras.execute_values(
                    cur,
                    "INSERT INTO players (uid, data) VALUES %s",
                    [(uid, json.dumps(pd)) for uid, pd in data.items()]
                )
                cur.close()
            except Exception as e:
                print(f"[DB] JSON migration failed: {e}", flush=True)
        return data if data else {}
    print("[DB] No data found in DB or JSON, returning empty", flush=True)
    return {}


def save_data(data):
    if _db_ready:
        try:
            cur = _db_conn.cursor()
            for uid, pd in data.items():
                cur.execute(
                    "INSERT INTO players (uid, data) VALUES (%s, %s) ON CONFLICT (uid) DO UPDATE SET data = EXCLUDED.data",
                    (uid, json.dumps(pd))
                )
            cur.close()
            return
        except Exception as e:
            print(f"[DB] save_data failed: {e}", flush=True)
    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)


DEFAULT_PLAYER = {
    "balance": 100, "last_daily": None,
    "multiplier_2x_expires": None, "multiplier_5x_expires": None,
    "pets": [], "equip_slots": 1, "inventory": {}, "luck_boost": 0,
    "xp": 0, "messages": 0, "commands": 0
}


def get_player(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = dict(DEFAULT_PLAYER)
    return data[uid]


PET_IMAGES = {
    "Red Fox": "https://cdn.discordapp.com/attachments/1520718205981687960/1520734186225533058/image.png",
    "Roe Deer": "https://cdn.discordapp.com/attachments/1520718205981687960/1520734314684223548/image.png",
    "Raccoon": "https://cdn.discordapp.com/attachments/1520718205981687960/1520734423153250375/image.png",
    "Gray Wolf": "https://cdn.discordapp.com/attachments/1520718205981687960/1520734630712443071/image.png",
    "Golden Eagle": "https://cdn.discordapp.com/attachments/1520718205981687960/1520735249091264665/image.png",
    "Desert Lizard": "https://cdn.discordapp.com/attachments/1520718205981687960/1528798492711981197/Desert_Lizard.webp",
    "Flamingo": "https://cdn.discordapp.com/attachments/1520718205981687960/1528798490874872018/Flamingo.webp",
    "Cheetah": "https://cdn.discordapp.com/attachments/1520718205981687960/1528798492288614552/Cheetah.jfif",
    "Lion": "https://cdn.discordapp.com/attachments/1520718205981687960/1528798491873251468/Lion.webp",
    "Golden Python": "https://cdn.discordapp.com/attachments/1520718205981687960/1528798491399426340/Golden_Python.png",
    "Arctic Hare": "https://cdn.discordapp.com/attachments/1520718205981687960/1528800336372957225/Arctic_Hare.webp",
    "Snowy Owl": "https://cdn.discordapp.com/attachments/1520718205981687960/1528800336037548164/Snowy_Ow.jfif",
    "Bengal Tiger": "https://cdn.discordapp.com/attachments/1520718205981687960/1528800337824321796/Bengal_Tige.webp",
    "Snow Leopard": "https://cdn.discordapp.com/attachments/1520718205981687960/1528800337480384672/Snow_Leopard.webp",
    "Golden Pheasant": "https://cdn.discordapp.com/attachments/1520718205981687960/1528800337043914852/Golden_Pheasant.webp",
}

PET_IMAGE_STYLES = {
    "Common": "icons",
    "Uncommon": "icons",
    "Rare": "icons",
    "Epic": "icons",
    "Legendary": "icons",
    "Gold": "icons",
}


def pet_image_url(pet_name, rarity="Common"):
    custom = PET_IMAGES.get(pet_name)
    if custom:
        return custom
    return f"https://api.dicebear.com/9.x/icons/png?seed={pet_name}&size=128&radius=10"


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
