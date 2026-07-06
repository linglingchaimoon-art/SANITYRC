from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests

from app.database import get_db
from app.models import ConnectedServer, User
from app.services.encryption import encrypt_value, decrypt_value
from app.services.security import decode_token

router = APIRouter(prefix="/servers", tags=["Servers"])


class ConnectServerRequest(BaseModel):
    server_name: str
    service_id: str
    nitrado_token: str


def get_current_user(
    authorization: str = Header(default=None, alias="Authorization"),
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


def get_user_connected_server(db: Session, user: User):
    server = (
        db.query(ConnectedServer)
        .filter(ConnectedServer.user_id == user.id)
        .first()
    )

    if not server:
        raise HTTPException(status_code=404, detail="No connected server found")

    return server


@router.post("/connect")
def connect_server(
    body: ConnectServerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    test_url = f"https://api.nitrado.net/services/{body.service_id}/gameservers"

    test_res = requests.get(
        test_url,
        headers={
            "Authorization": f"Bearer {body.nitrado_token}",
            "Accept": "application/json",
        },
        timeout=20,
    )

    if test_res.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid Nitrado API token")

    if test_res.status_code == 404:
        raise HTTPException(status_code=404, detail="Invalid Nitrado service ID")

    if test_res.status_code >= 400:
        raise HTTPException(
            status_code=400,
            detail="Could not verify Nitrado server connection",
        )

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

        return {"success": True, "message": "Server updated successfully."}

    server = ConnectedServer(
        user_id=user.id,
        server_name=body.server_name,
        service_id=body.service_id,
        nitrado_token_encrypted=encrypted_token,
        connected=True,
    )

    db.add(server)
    db.commit()

    return {"success": True, "message": "Server connected successfully."}


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
        return {"connected": False, "server": None}

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


@router.get("/status")
def get_connected_server_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    server = get_user_connected_server(db, user)
    token = decrypt_value(server.nitrado_token_encrypted)

    url = f"https://api.nitrado.net/services/{server.service_id}/gameservers"

    res = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        timeout=20,
    )

    if res.status_code >= 400:
        raise HTTPException(
            status_code=res.status_code,
            detail="Could not fetch Nitrado server status",
        )

    data = res.json()
    gameserver = data.get("data", {}).get("gameserver", {})

    return {
        "success": True,
        "server_name": server.server_name,
        "service_id": server.service_id,
        "status": gameserver.get("status"),
        "game": gameserver.get("game"),
        "hostname": gameserver.get("hostname"),
        "query": gameserver.get("query"),
        "raw": gameserver,
    }


@router.delete("/disconnect")
def disconnect_server(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    server = get_user_connected_server(db, user)

    db.delete(server)
    db.commit()

    return {
        "success": True,
        "message": "Server disconnected successfully.",
    }