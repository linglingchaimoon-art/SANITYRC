from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.live import live_manager

router = APIRouter(tags=["Live"])


@router.websocket("/ws/live")
async def live_socket(websocket: WebSocket):
    await live_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        live_manager.disconnect(websocket)