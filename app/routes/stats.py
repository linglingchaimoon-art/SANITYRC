from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import requests

from app.database import get_db
from app.models import ConnectedServer, User
from app.services.encryption import decrypt_value
from app.services.security import decode_token

router = APIRouter(prefix="/stats", tags=["Stats"])


def get_current_user(
    authorization: str = Header(default=None, alias="authorization"),
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


@router.get("/live")
def get_live_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    connected_server = (
        db.query(ConnectedServer)
        .filter(ConnectedServer.user_id == user.id)
        .first()
    )

    if not connected_server:
        raise HTTPException(status_code=404, detail="No connected server found")

    nitrado_token = decrypt_value(connected_server.nitrado_token_encrypted)

    url = f"https://api.nitrado.net/services/{connected_server.service_id}/gameservers"

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {nitrado_token}",
            "Accept": "application/json",
        },
        timeout=20,
    )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail="Could not fetch connected server stats",
        )

    data = response.json()
    gs = data["data"]["gameserver"]
    host = gs.get("hostsystems", {}).get("linux", {})

    return {
        "online": gs.get("status") == "started",
        "server_status": gs.get("status", "unknown"),
        "servername": connected_server.server_name or host.get("servername") or "Sanity RC",
        "hostname": host.get("hostname") or gs.get("hostname") or "Nitrado",
        "game": gs.get("game_human") or "Rust Console",
        "service_id": connected_server.service_id,
        "ip": gs.get("ip"),
        "port": gs.get("port"),
        "query_port": gs.get("query_port"),
        "slots": gs.get("slots", 100),
        "players": 0,
        "max_players": gs.get("slots", 100),
        "has_rcon": gs.get("game_specific", {}).get("features", {}).get("has_rcon", False),
    }