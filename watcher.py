"""
watcher.py
----------
Watches cowrie.json log for new lines in real time.
Run this alongside app.py:
    Terminal 1: python app.py
    Terminal 2: python watcher.py

For TESTING (Windows/local): watches data/cowrie.log
For PRODUCTION (Linux VPS with real Cowrie): change LOG_PATH below
"""

import time
import json
import os

from processor import extract_features
from ml_model import predict
from db import init_db, insert_log
from alerts import check_alert
from ai_engine import simulate_command

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------
# CHANGE THIS PATH when Cowrie is running on your Linux VPS:
# LOG_PATH = "/home/youruser/cowrie/var/log/cowrie/cowrie.json"
# ---------------------------------------------------------------
LOG_PATH = os.path.join(BASE_DIR, "data", "cowrie.log")

init_db()

print(f"[*] Watcher started. Monitoring: {LOG_PATH}")
print("[*] Waiting for new attack entries...\n")

# Wait for the log file to exist (Cowrie may not have started yet)
while not os.path.exists(LOG_PATH):
    print(f"[!] Log file not found: {LOG_PATH} — retrying in 5s...")
    time.sleep(5)

with open(LOG_PATH, "r") as f:
    # Jump to end — ignore entries already processed
    f.seek(0, 2)

    while True:
        line = f.readline()

        if not line:
            time.sleep(1)
            continue

        line = line.strip()
        if not line:
            continue

        try:
            log = json.loads(line)

            # Cowrie logs many event types — only process command input events
            event_id = log.get("eventid", "")
            if event_id not in ("cowrie.command.input", ""):
                continue

            ip = log.get("src_ip", "unknown")
            command = log.get("input", "").strip()

            if not command:
                continue

            features = extract_features(log)
            prediction = predict(features)

            insert_log(ip, command, prediction)
            check_alert(ip, prediction)

            response = simulate_command(command)
            print(f"[+] {ip} | {command!r} → {prediction} | fake reply: {response}")

        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"[!] Error processing line: {e}")
