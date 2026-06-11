from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ai_engine.utils.logger import get_structured_logger

logger = get_structured_logger("backend.websockets")
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"New client socket connected. Pool size: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(
            f"Client socket disconnected. Pool size: {len(self.active_connections)}"
        )

    async def broadcast_telemetry(self, message: dict):
        """
        Sends real-time telemetry updates to all connected web clients.
        """
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                # Handle connection issues gracefully
                logger.error(f"Error broadcasting socket message: {e}")


manager = ConnectionManager()


@router.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection active and listen for incoming messages if any
            data = await websocket.receive_text()
            # Echo or process incoming socket commands
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
