"""
processor.py
------------
Works with both real Cowrie JSON fields and test log fields.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------
# CHANGE THIS when Cowrie is on your Linux VPS:
# LOG_PATH = "/home/youruser/cowrie/var/log/cowrie/cowrie.json"
# ---------------------------------------------------------------
LOG_PATH = os.path.join(BASE_DIR, "data", "cowrie.log")


def parse_logs():
    logs = []
    try:
        with open(LOG_PATH) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    log = json.loads(line)
                    event_id = log.get("eventid", "")
                    if event_id and event_id != "cowrie.command.input":
                        continue
                    logs.append(log)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"[!] Log file not found: {LOG_PATH}")
    return logs


def extract_features(log):
    command = log.get("input", "")
    failed = log.get("failed_attempts", 0) or log.get("login_attempts", 0)
    return [len(command), int(failed), len(command.split())]
