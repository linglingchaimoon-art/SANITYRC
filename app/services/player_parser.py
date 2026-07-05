def parse_players_output(output: str):
    players = []

    lines = output.replace("\\n", "\n").splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if "id ;name" in line:
            continue

        if "Executing console" in line:
            continue

        if ";" not in line:
            continue

        parts = [p.strip() for p in line.split(";")]

        if len(parts) < 3:
            continue

        player_id = parts[0]
        name = parts[1]
        ping = parts[2]

        if not name:
            continue

        players.append({
            "id": player_id,
            "name": name,
            "ping": int(ping) if ping.isdigit() else None,
            "platform": "Unknown",
            "status": "Online",
            "health": 100,
            "grid": "Unknown",
            "time": "Live",
            "role": "Player"
        })

    return players