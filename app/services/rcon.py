import json
import websocket


def send_rcon_command(ip: str, port: int, password: str, command: str):
    url = f"ws://{ip}:{port}/{password}"

    ws = None

    try:
        ws = websocket.create_connection(
            url,
            timeout=20,
            enable_multithread=True,
        )

        packet = {
            "Identifier": 1,
            "Message": command,
            "Name": "SanityRC",
        }

        ws.send(json.dumps(packet))

        try:
            response = ws.recv()
            return json.loads(response)
        except Exception:
            return {
                "status": "sent",
                "message": "Command sent, but no response was returned.",
            }

    finally:
        if ws:
            try:
                ws.close()
            except Exception:
                pass