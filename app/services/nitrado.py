import requests
from fastapi import HTTPException

from app.config import NITRADO_TOKEN, BASE_URL


def nitrado_request(method: str, endpoint: str, json=None):
    url = BASE_URL + endpoint

    headers = {
        "Authorization": f"Bearer {NITRADO_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print("=" * 50)
    print("NITRADO REQUEST")
    print("METHOD:", method)
    print("URL:", url)
    print("BODY:", json)
    print("=" * 50)

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=json,
        timeout=30,
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )

    try:
        return response.json()
    except ValueError:
        return {
            "success": True,
            "raw": response.text,
        }


# --------------------------------------------------
# SERVER INFORMATION
# --------------------------------------------------

def get_services():
    return nitrado_request(
        "GET",
        "/services",
    )


def get_gameserver(server_id: str):
    return nitrado_request(
        "GET",
        f"/services/{server_id}/gameservers",
    )


# --------------------------------------------------
# COMMANDS
# --------------------------------------------------

def send_command(server_id: str, command: str):
    return nitrado_request(
        "POST",
        f"/services/{server_id}/gameservers/command",
        json={"command": command},
    )
    """
    Sends any command to the gameserver.

    Example:
    say Hello World
    status
    players
    kick Player
    ban Player
    """

    return nitrado_request(
        "POST",
        f"/services/{server_id}/gameservers/commands",
        json={
            "command": command
        },
    )


# --------------------------------------------------
# SERVER POWER
# --------------------------------------------------

def start_server(server_id: str):
    return nitrado_request(
        "POST",
        f"/services/{server_id}/gameservers/start",
    )


def stop_server(server_id: str):
    return nitrado_request(
        "POST",
        f"/services/{server_id}/gameservers/stop",
    )


def restart_server(server_id: str):
    return nitrado_request(
        "POST",
        f"/services/{server_id}/gameservers/restart",
    )


# --------------------------------------------------
# FILE SERVER
# --------------------------------------------------

def get_file_server(server_id: str):
    return nitrado_request(
        "GET",
        f"/services/{server_id}/gameservers/file_server",
    ) 