from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.config import PRIVATE_API_KEY
from app.services.player_parser import parse_players_output

router = APIRouter(prefix="/players", tags=["Players"])

LATEST_PLAYERS = []


class PlayerOutput(BaseModel):
    output: str


def check_key(x_api_key: str):
    if x_api_key != PRIVATE_API_KEY:
        raise HTTPException(401, "Invalid API key")


@router.get("/online")
def get_online_players(x_api_key: str = Header(alias="x-api-key")):
    check_key(x_api_key)

    return {
        "count": len(LATEST_PLAYERS),
        "players": LATEST_PLAYERS
    }


@router.post("/parse")
def parse_players(
    body: PlayerOutput,
    x_api_key: str = Header(alias="x-api-key")
):
    check_key(x_api_key)

    global LATEST_PLAYERS
    LATEST_PLAYERS = parse_players_output(body.output)

    return {
        "count": len(LATEST_PLAYERS),
        "players": LATEST_PLAYERS
    }