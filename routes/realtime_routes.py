from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from service.dining_service import DiningService
from service.realtime_service import realtime_manager
from service.security_service import resolve_access_token
from utils.data_base_engine import get_database


realtime_router = APIRouter(tags=["Realtime"])


@realtime_router.websocket("/ws/table-sessions/{session_id}")
async def table_session_socket(
    websocket: WebSocket,
    session_id: str,
    token: str,
    database: Session = Depends(get_database),
):
    try:
        DiningService(database).verify_session_token(token, session_id)
    except Exception:
        await websocket.close(code=4401, reason="Invalid table session token")
        return
    channel = f"table:{session_id}"
    await realtime_manager.connect(channel, websocket)
    await websocket.send_json({"event": "connected", "channel": channel})
    try:
        while True:
            message = await websocket.receive_text()
            if message.lower() == "ping":
                await websocket.send_json({"event": "pong"})
    except WebSocketDisconnect:
        await realtime_manager.disconnect(channel, websocket)


@realtime_router.websocket("/ws/restaurants/{restaurant_id}/kitchen")
async def kitchen_socket(
    websocket: WebSocket,
    restaurant_id: int,
    token: str,
    database: Session = Depends(get_database),
):
    try:
        user = resolve_access_token(token, database)
        if user.user_type not in {"admin", "manager", "kitchen", "waiter", "cashier"}:
            raise ValueError
        if user.user_type != "admin" and user.restaurant_id != restaurant_id:
            raise ValueError
    except Exception:
        await websocket.close(code=4403, reason="Not authorized for this restaurant")
        return
    channel = f"restaurant:{restaurant_id}"
    await realtime_manager.connect(channel, websocket)
    await websocket.send_json({"event": "connected", "channel": channel})
    try:
        while True:
            message = await websocket.receive_text()
            if message.lower() == "ping":
                await websocket.send_json({"event": "pong"})
    except WebSocketDisconnect:
        await realtime_manager.disconnect(channel, websocket)
