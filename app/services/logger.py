from datetime import datetime, timezone
import json
import os

LOG_FILE = "logs.json"


def save_log(
    category: str,
    role: str,
    admin: str,
    action: str,
    success: bool,
    message: str
):
    log = {
        "time": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "role": role,
        "admin": admin,
        "action": action,
        "success": success,
        "message": message
    }

    logs = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

    return log