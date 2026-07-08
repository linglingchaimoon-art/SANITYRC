from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rcon import send_rcon_command

router = APIRouter(prefix="/rcon", tags=["RCON"])


class RconRequest(BaseModel):
    ip: str
    port: int
    password: str
    command: str


@router.post("/send")
def send_command(body: RconRequest):
    try:
        response = send_rcon_command(
            body.ip,
            body.port,
            body.password,
            body.command,
        )

        return {
            "success": True,
            "command": body.command,
            "response": response,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RCON failed: {str(e)}",
        )