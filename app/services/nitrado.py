import requests
from fastapi import HTTPException

from app.config import BASE_URL, NITRADO_TOKEN


def nitrado_request(
    method: str,
    endpoint: str,
    json: dict | None = None,
    token: str | None = None,
):
    """
    Send a request to the Nitrado API.

    `token` can be supplied for a user-owned encrypted token.
    Otherwise the global NITRADO_TOKEN from environment variables is used.
    """

    api_token = token or NITRADO_TOKEN

    if not api_token:
        raise HTTPException(
            status_code=500,
            detail="Nitrado API token is not configured.",
        )

    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=json,
            timeout=30,
        )
    except requests.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Nitrado API request timed out.",
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach Nitrado API: {exc}",
        )

    if response.status_code >= 400:
        try:
            error_data = response.json()
            detail = (
                error_data.get("message")
                or error_data.get("detail")
                or response.text
            )
        except ValueError:
            detail = response.text or "Nitrado API request failed."

        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )

    if not response.content:
        return {
            "success": True,
            "status_code": response.status_code,
        }

    try:
        return response.json()
    except ValueError:
        return {
            "success": True,
            "status_code": response.status_code,
            "raw": response.text,
        }


# --------------------------------------------------
# SERVER INFORMATION
# --------------------------------------------------

def get_services(token: str | None = None):
    return nitrado_request(
        "GET",
        "/services",
        token=token,
    )


def get_gameserver(server_id: str, token: str | None = None):
    return nitrado_request(
        "GET",
        f"/services/{server_id}/gameservers",
        token=token,
    )


def get_games(server_id: str, token: str | None = None):
    return nitrado_request(
        "GET",
        f"/services/{server_id}/gameservers/games",
        token=token,
    )


# --------------------------------------------------
# COMMANDS
# --------------------------------------------------

def send_command(
    server_id: str,
    command: str,
    token: str | None = None,
):
    if not command or not command.strip():
        raise HTTPException(
            status_code=400,
            detail="Command cannot be empty.",
        )

    return nitrado_request(
        "POST",
        f"/services/{server_id}/gameservers/command",
        json={"command": command.strip()},
        token=token,
    )


# --------------------------------------------------
# SERVER POWER
# --------------------------------------------------

def start_server(
    server_id: str,
    token: str | None = None,
    game: str = "rustconsole",
):
    return nitrado_request(
        "POST",
        f"/services/{server_id}/gameservers/games/start?game={game}",
        token=token,
    )


def stop_server(
    server_id: str,
    token: str | None = None,
):
    return nitrado_request(
        "POST",
        f"/services/{server_id}/gameservers/games/stop",
        token=token,
    )


def restart_server(
    server_id: str,
    token: str | None = None,
    game: str = "rustconsole",
):
    """
    Rust Console restart is performed by stopping and starting the service.
    """

    stop_response = stop_server(
        server_id=server_id,
        token=token,
    )

    start_response = start_server(
        server_id=server_id,
        token=token,
        game=game,
    )

    return {
        "success": True,
        "message": "Restart requested.",
        "stop": stop_response,
        "start": start_response,
    }


# --------------------------------------------------
# FILE SERVER
# --------------------------------------------------

def get_file_server(
    server_id: str,
    token: str | None = None,
):
    return nitrado_request(
        "GET",
        f"/services/{server_id}/gameservers/file_server",
        token=token,
    )