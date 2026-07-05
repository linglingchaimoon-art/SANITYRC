from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ConnectedServer
from app.services.encryption import encrypt_value

router = APIRouter(prefix="/servers", tags=["Servers"])


class ConnectServerRequest(BaseModel):
    user_id: int
    server_name: str
    service_id: str
    nitrado_token: str


@router.post("/connect")
def connect_server(
    body: ConnectServerRequest,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(ConnectedServer)
        .filter(ConnectedServer.user_id == body.user_id)
        .first()
    )

    encrypted_token = encrypt_value(body.nitrado_token)

    if existing:
        existing.server_name = body.server_name
        existing.service_id = body.service_id
        existing.nitrado_token_encrypted = encrypted_token
        existing.connected = True

        db.commit()

        return {
            "success": True,
            "message": "Server updated successfully."
        }

    server = ConnectedServer(
        user_id=body.user_id,
        server_name=body.server_name,
        service_id=body.service_id,
        nitrado_token_encrypted=encrypted_token,
    )

    db.add(server)
    db.commit()

    return {
        "success": True,
        "message": "Server connected successfully."
    }