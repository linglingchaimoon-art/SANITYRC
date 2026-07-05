from fastapi import APIRouter, Header, HTTPException

from app.config import PRIVATE_API_KEY, SERVICE_ID
from app.services.nitrado import nitrado_request

router = APIRouter(prefix="/stats", tags=["Stats"])


def check_key(x_api_key: str):
    if x_api_key != PRIVATE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/live")
def get_live_stats():

    response = nitrado_request(
        "GET",
        f"/services/{SERVICE_ID}/gameservers"
    )

    gs = response["data"]["gameserver"]
    host = gs.get("hostsystems", {}).get("linux", {})

    return {
        "online": gs.get("status") == "started",
        "server_status": gs.get("status", "unknown"),
        "servername": host.get("servername") or gs.get("username") or "Sanity RC",
        "hostname": host.get("hostname") or "Unknown",
        "game": gs.get("game_human") or "Rust Console",
        "service_id": gs.get("service_id"),
        "ip": gs.get("ip"),
        "port": gs.get("port"),
        "query_port": gs.get("query_port"),
        "slots": gs.get("slots", 100),
        "players": 0,
        "max_players": gs.get("slots", 100),
        "has_rcon": gs.get("game_specific", {}).get("features", {}).get("has_rcon", False),
    }