import os
import json

DATA_FILE = "data/economy.json"

mongo = None
if os.getenv("MONGO_URI"):
    from pymongo import MongoClient
    mongo = MongoClient(os.getenv("MONGO_URI"))
    db = mongo.get_database("cashempire")
    col = db["players"]


def load_data():
    if mongo:
        data = {}
        for doc in col.find():
            data[doc["_id"]] = {k: v for k, v in doc.items() if k != "_id"}
        return data
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save_data(data):
    if mongo:
        col.delete_many({})
        if data:
            col.insert_many([{"_id": uid, **pd} for uid, pd in data.items()])
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
