"""WebSocket router for real-time alert streaming.

Clients connect via ws://host:8000/api/ws/alerts?token=JWT
and receive new alerts as JSON messages in real-time.
"""
import logging
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger("socforge.websocket")
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections with heartbeat."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(
            "WebSocket client connected (total: %d)", len(self.active_connections)
        )

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(
            "WebSocket client disconnected (total: %d)", len(self.active_connections)
        )

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        payload = json.dumps(message, default=str)
        disconnected = []
        async with self._lock:
            for ws in self.active_connections:
                try:
                    await ws.send_text(payload)
                except Exception:
                    disconnected.append(ws)
        for ws in disconnected:
            await self.disconnect(ws)

    @property
    def client_count(self) -> int:
        return len(self.active_connections)


# Module-level singleton
manager = ConnectionManager()


def _verify_ws_token(token: str) -> dict:
    """Verify JWT token for WebSocket connections."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if not payload.get("sub"):
            return {}
        return payload
    except JWTError:
        return {}


@router.websocket("/alerts")
async def ws_alerts(websocket: WebSocket, token: str = Query(default="")):
    """WebSocket endpoint for real-time alert streaming.

    Connect: ws://host:8000/api/ws/alerts?token=<JWT>
    """
    # Authenticate
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return
    payload = _verify_ws_token(token)
    if not payload:
        await websocket.close(code=4003, reason="Invalid token")
        return

    await manager.connect(websocket)
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "SOCForge alert stream active",
            "user": payload.get("sub"),
            "timestamp": datetime.utcnow().isoformat(),
        })
        # Keep connection alive — listen for pings
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat(),
                    "clients": manager.client_count,
                })
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)


async def broadcast_alert(alert: Any):
    """Broadcast a new alert to all connected WebSocket clients."""
    await manager.broadcast({
        "type": "new_alert",
        "data": {
            "id": str(alert.id) if hasattr(alert, "id") else None,
            "title": getattr(alert, "title", ""),
            "severity": getattr(alert, "severity", ""),
            "source_ip": getattr(alert, "source_ip", ""),
            "dest_ip": getattr(alert, "dest_ip", ""),
            "mitre_tactic": getattr(alert, "mitre_tactic", ""),
            "mitre_technique": getattr(alert, "mitre_technique", ""),
            "event_count": getattr(alert, "event_count", 0),
        },
        "timestamp": datetime.utcnow().isoformat(),
    })


async def broadcast_incident(incident: Any):
    """Broadcast a new incident to all connected WebSocket clients."""
    await manager.broadcast({
        "type": "new_incident",
        "data": {
            "id": str(incident.id) if hasattr(incident, "id") else None,
            "title": getattr(incident, "title", ""),
            "severity": getattr(incident, "severity", ""),
            "alert_count": getattr(incident, "alert_count", 0),
            "kill_chain_phase": getattr(incident, "kill_chain_phase", ""),
        },
        "timestamp": datetime.utcnow().isoformat(),
    })
