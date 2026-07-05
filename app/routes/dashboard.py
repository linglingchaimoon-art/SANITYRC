from fastapi import APIRouter, Header, HTTPException

from app.config import PRIVATE_API_KEY
from app.services.nitrado import nitrado_request

router = APIRouter(prefix="/dashboard")


def check_key(x_api_key: str):
    if x_api_key != PRIVATE_API_KEY:
        raise HTTPException(401, "Invalid API key")


@router.get("/summary")
def dashboard_summary(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    data = nitrado_request("GET", "/services")
    services = data["data"]["services"]

    service = services[0]
    details = service.get("details", {})

    return {
        "status": service.get("status"),
        "service_id": service.get("id"),
        "server_name": details.get("name"),
        "address": details.get("address"),
        "type": service.get("type_human"),
        "game": details.get("game"),
        "slots": details.get("slots"),
        "websocket_token_available": bool(service.get("websocket_token"))
    }