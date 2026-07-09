from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests

from app.database import get_db
from app.models import ConnectedServer, User
from app.services.encryption import decrypt_value
from app.services.security import decode_token
from app.services.logger import save_log

router = APIRouter(prefix="/nitrado")


class CommandRequest(BaseModel):
   command: str


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


def get_server_owner_id(user: User):
   return user.owner_user_id or user.id


def require_owner(user: User):
   if str(user.role).lower() != "owner":
       raise HTTPException(status_code=403, detail="Owner only action")


def get_connected_server(db: Session, user: User):
   owner_id = get_server_owner_id(user)

   server = (
       db.query(ConnectedServer)
       .filter(ConnectedServer.user_id == owner_id)
       .first()
   )

   if not server:
       raise HTTPException(status_code=404, detail="No connected server found")

   token = decrypt_value(server.nitrado_token_encrypted)

   return server, token


def nitrado_user_request(method: str, server_id: str, token: str, endpoint: str):
   url = f"https://api.nitrado.net/services/{server_id}{endpoint}"

   response = requests.request(
       method,
       url,
       headers={
           "Authorization": f"Bearer {token}",
           "Accept": "application/json",
           "Content-Type": "application/json",
       },
       timeout=30,
   )

   if response.status_code >= 400:
       raise HTTPException(status_code=response.status_code, detail=response.text)

   try:
       return response.json()
   except Exception:
       return {"success": True, "raw": response.text}


@router.get("/server")
def server_status(
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user),
):
   server, token = get_connected_server(db, user)

   response = nitrado_user_request(
       "GET",
       server.service_id,
       token,
       "/gameservers",
   )

   status = response["data"]["gameserver"]["status"]

   save_log(
       category="server",
       role=user.role,
       admin=user.email,
       action="status",
       success=True,
       message=f"Checked server status ({status})",
   )

   return response


@router.post("/start")
def start_server(
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user),
):
   require_owner(user)
   server, token = get_connected_server(db, user)

   response = nitrado_user_request(
       "POST",
       server.service_id,
       token,
       "/gameservers/games/start?game=rustconsole",
   )

   save_log(
       category="server",
       role=user.role,
       admin=user.email,
       action="start",
       success=True,
       message=f"Started server {server.server_name}",
   )

   return response


@router.post("/stop")
def stop_server(
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user),
):
   require_owner(user)
   server, token = get_connected_server(db, user)

   response = nitrado_user_request(
       "POST",
       server.service_id,
       token,
       "/gameservers/games/stop",
   )

   save_log(
       category="server",
       role=user.role,
       admin=user.email,
       action="stop",
       success=True,
       message=f"Stopped server {server.server_name}",
   )

   return response


@router.post("/restart")
def restart_server(
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user),
):
   require_owner(user)
   server, token = get_connected_server(db, user)

   stop_response = nitrado_user_request(
       "POST",
       server.service_id,
       token,
       "/gameservers/games/stop",
   )

   start_response = nitrado_user_request(
       "POST",
       server.service_id,
       token,
       "/gameservers/games/start?game=rustconsole",
   )

   save_log(
       category="server",
       role=user.role,
       admin=user.email,
       action="restart",
       success=True,
       message=f"Restarted server {server.server_name}",
   )

   return {
       "status": "success",
       "message": "Restart requested",
       "stop": stop_response,
       "start": start_response,
   }


@router.post("/command")
def send_server_command(
   body: CommandRequest,
   db: Session = Depends(get_db),
   user: User = Depends(get_current_user),
):
   server, token = get_connected_server(db, user)

   response = nitrado_user_request(
       "POST",
       server.service_id,
       token,
       "/gameservers/command",
   )

   save_log(
       category="console",
       role=user.role,
       admin=user.email,
       action="command",
       success=True,
       message=f"Command requested: {body.command}",
   )

   return {
       "success": True,
       "message": "Command sent successfully.",
       "response": response,
   }