from fastapi import APIRouter, Header, HTTPException
import json
import os

from app.config import PRIVATE_API_KEY

router = APIRouter(prefix="/logs")


def check_key(x_api_key: str):
    if x_api_key != PRIVATE_API_KEY:
        raise HTTPException(401, "Invalid API key")


@router.get("/")
def get_logs(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    if not os.path.exists("logs.json"):
        return []

    with open("logs.json", "r") as f:
        return json.load(f)