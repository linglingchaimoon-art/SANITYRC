from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.config import PRIVATE_API_KEY, SERVICE_ID
from app.services.nitrado import nitrado_request
from app.services.logger import save_log

router = APIRouter(prefix="/console", tags=["Console"])


class ConsoleCommand(BaseModel):
    command: str


def check_key(x_api_key: str):
    if x_api_key != PRIVATE_API_KEY:
        raise HTTPException(401, "Invalid API key")


@router.post("/send")
def send_console(
    body: ConsoleCommand,
    x_api_key: str = Header(alias="x-api-key")
):
    check_key(x_api_key)

    command = body.command.strip()

    response = nitrado_request(
        "POST",
        f"/services/{SERVICE_ID}/gameservers/command",
        json={"command": command}
    )

    save_log(
        category="console",
        role="Owner",
        admin="TJ",
        action="command",
        success=True,
        message=f"Sent command: {command}"
    )

    return {
        "success": True,
        "output": f"Command sent: {command}",
        "nitrado": response
    }