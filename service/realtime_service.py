import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class RealtimeManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[channel].add(websocket)

    async def disconnect(self, channel: str, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(channel)
            if connections is None:
                return
            connections.discard(websocket)
            if not connections:
                self._connections.pop(channel, None)

    async def broadcast(self, channel: str, event: dict[str, Any]) -> None:
        async with self._lock:
            connections = list(self._connections.get(channel, set()))
        disconnected: list[WebSocket] = []
        for websocket in connections:
            try:
                await websocket.send_json(event)
            except Exception:
                disconnected.append(websocket)
        for websocket in disconnected:
            await self.disconnect(channel, websocket)

    def connection_count(self, channel: str) -> int:
        return len(self._connections.get(channel, set()))


realtime_manager = RealtimeManager()
