from fastapi import APIRouter, Header, HTTPException
from app.config import PRIVATE_API_KEY, SERVICE_ID
from app.services.nitrado import nitrado_request

router = APIRouter(prefix="/files")


def check_key(x_api_key: str):
    if x_api_key != PRIVATE_API_KEY:
        raise HTTPException(401, "Invalid API key")


@router.get("/list")
def list_files(path: str = "/", x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    return nitrado_request(
        "GET",
        f"/services/{SERVICE_ID}/gameservers/file_server/list?dir={path}"
    )