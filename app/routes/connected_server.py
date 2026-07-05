from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ConnectedServer, User
from app.services.encryption import encrypt_value
from app.services.security import decode_token

router = APIRouter(prefix="/servers", tags=["Servers"])


class ConnectServerRequest(BaseModel):
    server_name: str
    service_id: str
    nitrado_token: str


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/connect")
def connect_server(
    body: ConnectServerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    encrypted_token = encrypt_value(body.nitrado_token)

    existing = (
        db.query(ConnectedServer)
        .filter(ConnectedServer.user_id == user.id)
        .first()
    )

    if existing:
        existing.server_name = body.server_name
        existing.service_id = body.service_id
        existing.nitrado_token_encrypted = encrypted_token
        existing.connected = True

        db.commit()

        return {
            "success": True,
            "message": "Server updated successfully.",
        }

    server = ConnectedServer(
        user_id=user.id,
        server_name=body.server_name,
        service_id=body.service_id,
        nitrado_token_encrypted=encrypted_token,
        connected=True,
    )

    db.add(server)
    db.commit()

    return {
        "success": True,
        "message": "Server connected successfully.",
    }


@router.get("/me")
def get_my_server(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    server = (
        db.query(ConnectedServer)
        .filter(ConnectedServer.user_id == user.id)
        .first()
    )

    if not server:
        return {
            "connected": False,
            "server": None,
        }

    return {
        "connected": server.connected,
        "server": {
            "id": server.id,
            "server_name": server.server_name,
            "service_id": server.service_id,
            "token_preview": "••••••••••••",
            "created_at": server.created_at,
        },
    }


@router.delete("/disconnect")
def disconnect_server(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    server = (
        db.query(ConnectedServer)
        .filter(ConnectedServer.user_id == user.id)
        .first()
    )

    if not server:
        raise HTTPException(status_code=404, detail="No connected server found")

    db.delete(server)
    db.commit()

    return {
        "success": True,
        "message": "Server disconnected successfully.",
    }