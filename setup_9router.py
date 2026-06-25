#!/usr/bin/env python3
"""Bulk insert BTL API keys into 9router SQLite database."""
import sqlite3, json, uuid, os

DB_PATH = os.path.expanduser("~/.9router/db/data.sqlite")
KEYS_FILE = os.path.expanduser("~/.hermes/btl-keys-active.txt")
BASE_URL = "https://api.badtheorylabs.com/v1"
MODEL = "deepseek-v4-pro"

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(KEYS_FILE), exist_ok=True)

# Copy keys to standard location
import shutil
shutil.copy("/opt/data/apikeys_only.txt", KEYS_FILE)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS providerNodes (
    id TEXT PRIMARY KEY, type TEXT, name TEXT, data TEXT,
    createdAt TEXT, updatedAt TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS providerConnections (
    id TEXT PRIMARY KEY, provider TEXT, authType TEXT, name TEXT,
    email TEXT, priority INTEGER, isActive INTEGER, data TEXT,
    createdAt TEXT, updatedAt TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS combos (
    id TEXT PRIMARY KEY, name TEXT, kind TEXT, models TEXT,
    createdAt TEXT, updatedAt TEXT)""")

cur.execute("DELETE FROM providerConnections WHERE data LIKE '%badtheorylabs%'")
cur.execute("DELETE FROM providerNodes WHERE data LIKE '%badtheorylabs%'")
cur.execute("DELETE FROM combos WHERE name = 'btl-deepseek'")

with open(KEYS_FILE) as f:
    keys = [l.strip() for l in f if l.strip().startswith('gw_')]

print(f"Inserting {len(keys)} BTL keys...")
members = []
ts = "2026-06-25T00:00:00Z"

for i, key in enumerate(keys, 1):
    node_id = f"openai-compatible-chat-{uuid.uuid4()}"
    conn_id = str(uuid.uuid4())

    cur.execute(
        "INSERT INTO providerNodes (id, type, name, data, createdAt, updatedAt) VALUES (?,?,?,?,?,?)",
        (node_id, 'openai-compatible', f'BTL DeepSeek {i}',
         json.dumps({"prefix": f"btl-{i}", "apiType": "chat", "baseUrl": BASE_URL, "apiKey": key}),
         ts, ts))

    cur.execute(
        "INSERT INTO providerConnections (id, provider, authType, name, email, priority, isActive, data, createdAt, updatedAt) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (conn_id, node_id, 'apikey', f'BTL DeepSeek {i}', '', 1, 1,
         json.dumps({
             "apiKey": key,
             "defaultModel": MODEL,
             "providerSpecificData": {
                 "prefix": f"btl-{i}",
                 "apiType": "chat",
                 "baseUrl": BASE_URL,
                 "nodeName": f"BTL DeepSeek {i}"
             },
             "testStatus": "untested",
             "backoffLevel": 0
         }),
         ts, ts))

    members.append(f"btl-{i}/{MODEL}")

cur.execute(
    "INSERT INTO combos (id, name, kind, models, createdAt, updatedAt) VALUES (?,?,?,?,?,?)",
    (str(uuid.uuid4()), 'btl-deepseek', 'round-robin', json.dumps(members), ts, ts))

conn.commit()
conn.close()
print(f"Done! {len(keys)} providers + connections + combo 'btl-deepseek'")
