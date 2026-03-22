"""
WebSocket 心跳端点
"""
import json

from fastapi import APIRouter, WebSocket, Query
from jose import JWTError, jwt
from starlette.websockets import WebSocketDisconnect

from app.config import settings
from app.database import SessionLocal
from app.models.models import User
from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/api/ws/heartbeat")
async def websocket_heartbeat(websocket: WebSocket, token: str = Query(...)):
    """WebSocket 心跳端点：验证 Token，注册连接，处理心跳消息"""

    # Step 1: 验证 JWT Token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            await websocket.close(code=4001, reason="Token 无效")
            return
    except JWTError:
        await websocket.close(code=4001, reason="Token 无效或已过期")
        return

    # Step 2: 查询用户
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
    finally:
        db.close()

    if user is None:
        await websocket.close(code=4002, reason="用户不存在")
        return

    # Step 3: 接受连接并注册
    await websocket.accept()
    await manager.connect(user.id, websocket)

    # Step 4: 心跳循环
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                # 非 JSON 消息，忽略
                continue

            if isinstance(data, dict) and data.get("type") == "ping":
                manager.heartbeat(user.id, websocket)
                await websocket.send_json({"type": "pong"})
            # 其他消息忽略，不断开连接不更新心跳
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        # Step 5: 清理连接
        await manager.disconnect(user.id, websocket)
