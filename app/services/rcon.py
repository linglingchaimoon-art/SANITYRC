import json
import websocket


def send_rcon_command(ip: str, port: int, password: str, command: str):
    url = f"ws://{ip}:{port}/{password}"

    ws = websocket.create_connection(url, timeout=10)

    packet = {
        "Identifier": 1,
        "Message": command,
        "Name": "SanityRC",
    }

    ws.send(json.dumps(packet))
    response = ws.recv()
    ws.close()

    return json.loads(response)