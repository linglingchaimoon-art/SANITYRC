from fastapi import APIRouter, Header, HTTPException

from app.config import PRIVATE_API_KEY, SERVICE_ID
from app.services.nitrado import nitrado_request
from app.services.logger import save_log


from pydantic import BaseModel
from app.services.nitrado import send_command

router = APIRouter(prefix="/nitrado")


def check_key(x_api_key: str):
    if x_api_key != PRIVATE_API_KEY:
        raise HTTPException(401, "Invalid API key")


CURRENT_ADMIN = "TJ"
CURRENT_ROLE = "Owner"

class CommandRequest(BaseModel):
    command: str

@router.get("/server")
def server_status(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    response = nitrado_request(
        "GET",
        f"/services/{SERVICE_ID}/gameservers"
    )

    status = response["data"]["gameserver"]["status"]

    save_log(
        category="server",
        role=CURRENT_ROLE,
        admin=CURRENT_ADMIN,
        action="status",
        success=True,
        message=f"Checked server status ({status})"
    )

    return response


@router.post("/start")
def start_server(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    response = nitrado_request(
        "POST",
        f"/services/{SERVICE_ID}/gameservers/games/start?game=rustconsole"
    )

    save_log(
        category="server",
        role=CURRENT_ROLE,
        admin=CURRENT_ADMIN,
        action="start",
        success=True,
        message="Started the Rust Console server"
    )

    return response


@router.post("/stop")
def stop_server(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    response = nitrado_request(
        "POST",
        f"/services/{SERVICE_ID}/gameservers/games/stop"
    )

    save_log(
        category="server",
        role=CURRENT_ROLE,
        admin=CURRENT_ADMIN,
        action="stop",
        success=True,
        message="Stopped the Rust Console server"
    )

    return response


@router.post("/restart")
def restart_server(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    response = nitrado_request(
        "POST",
        f"/services/{SERVICE_ID}/gameservers/games/start?game=rustconsole"
    )

    save_log(
        category="server",
        role=CURRENT_ROLE,
        admin=CURRENT_ADMIN,
        action="restart",
        success=True,
        message="Restarted the Rust Console server"
    )

    return {
        "status": "success",
        "message": "Restart requested",
        "start": response
    }


@router.get("/games")
def get_games(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    response = nitrado_request(
        "GET",
        f"/services/{SERVICE_ID}/gameservers/games"
    )

    save_log(
        category="server",
        role=CURRENT_ROLE,
        admin=CURRENT_ADMIN,
        action="games",
        success=True,
        message="Viewed available games"
    )

    return response


@router.get("/services")
def get_services(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    response = nitrado_request(
        "GET",
        "/services"
    )

    save_log(
        category="server",
        role=CURRENT_ROLE,
        admin=CURRENT_ADMIN,
        action="services",
        success=True,
        message="Viewed services list"
    )
    return response


@router.post("/command")
def send_server_command(
    body: CommandRequest,
    x_api_key: str = Header(alias="x-api-key"),
):
    check_key(x_api_key)

    response = send_command(
        SERVICE_ID,
        body.command,
    )

    save_log(
        category="console",
        role=CURRENT_ROLE,
        admin=CURRENT_ADMIN,
        action="command",
        success=True,
        message=f"Executed command: {body.command}",
    )

    return {
        "success": True,
        "message": "Command sent successfully.",
        "response": response,
    }