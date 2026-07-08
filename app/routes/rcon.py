import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rcon import send_rcon_command

router = APIRouter(prefix="/rcon", tags=["RCON"])


class RconRequest(BaseModel):
    ip: str
    port: int
    password: str
    command: str


class PanelCommandRequest(BaseModel):
    command: str


@router.post("/send")
def send_command(body: RconRequest):
    """
    Manual RCON endpoint (Swagger testing)
    """

    try:
        response = send_rcon_command(
            ip=body.ip,
            port=body.port,
            password=body.password,
            command=body.command,
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


@router.post("/panel/send")
def send_panel_command(body: PanelCommandRequest):
    """
    Dashboard endpoint.
    Uses Railway environment variables.
    """

    ip = os.getenv("RCON_IP")
    port = os.getenv("RCON_PORT")
    password = os.getenv("RCON_PASSWORD")

    if not ip:
        raise HTTPException(
            status_code=500,
            detail="RCON_IP not configured.",
        )

    if not port:
        raise HTTPException(
            status_code=500,
            detail="RCON_PORT not configured.",
        )

    if not password:
        raise HTTPException(
            status_code=500,
            detail="RCON_PASSWORD not configured.",
        )

    try:
        response = send_rcon_command(
            ip=ip,
            port=int(port),
            password=password,
            command=body.command,
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


@router.get("/status")
def rcon_status():
    """
    Simple endpoint to verify RCON configuration.
    """

    return {
        "configured": (
            os.getenv("RCON_IP") is not None
            and os.getenv("RCON_PORT") is not None
            and os.getenv("RCON_PASSWORD") is not None
        ),
        "ip": os.getenv("RCON_IP"),
        "port": os.getenv("RCON_PORT"),
    }