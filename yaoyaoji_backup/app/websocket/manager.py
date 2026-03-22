"""
WebSocket 连接管理器

维护所有 WebSocket 连接的内存映射，提供在线用户查询和超时清理功能。
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from fastapi import WebSocket


@dataclass
class UserConnection:
    """单个用户连接信息"""
    user_id: int
    websocket: WebSocket
    connected_at: datetime
    last_heartbeat: datetime


class ConnectionManager:
    """WebSocket 连接管理器（单例）

    维护 user_id → List[UserConnection] 映射，支持同一用户多设备连接。
    使用 asyncio.Lock 保证并发安全。
    """

    def __init__(self) -> None:
        self._connections: dict[int, list[UserConnection]] = {}
        self._lock = asyncio.Lock()

    def get_online_count(self) -> int:
        """获取在线用户数（去重）"""
        return len(self._connections)

    def get_online_user_ids(self) -> set[int]:
        """获取所有在线用户 ID 集合"""
        return set(self._connections.keys())

    def get_online_user_details(self) -> list[dict]:
        """获取所有在线用户的连接详情（user_id + 最早连接时间）"""
        result = []
        for user_id, connections in self._connections.items():
            earliest = min(c.connected_at for c in connections)
            result.append({"user_id": user_id, "connected_at": earliest})
        return result

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """注册新的 WebSocket 连接"""
        now = datetime.now()
        conn = UserConnection(
            user_id=user_id,
            websocket=websocket,
            connected_at=now,
            last_heartbeat=now,
        )
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = []
            self._connections[user_id].append(conn)

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """移除指定连接，若用户无其他连接则从映射中移除该用户"""
        async with self._lock:
            if user_id not in self._connections:
                return
            self._connections[user_id] = [
                c for c in self._connections[user_id]
                if c.websocket is not websocket
            ]
            if not self._connections[user_id]:
                del self._connections[user_id]

    def heartbeat(self, user_id: int, websocket: WebSocket) -> None:
        """更新指定连接的心跳时间"""
        if user_id not in self._connections:
            return
        for conn in self._connections[user_id]:
            if conn.websocket is websocket:
                conn.last_heartbeat = datetime.now()
                break

    async def cleanup_stale(self, timeout_seconds: int = 90) -> None:
        """清理超时连接

        移除所有 last_heartbeat 距当前时间超过 timeout_seconds 的连接，
        并调用 websocket.close() 关闭它们。
        """
        now = datetime.now()
        stale: list[tuple[int, WebSocket]] = []

        async with self._lock:
            for user_id, connections in list(self._connections.items()):
                for conn in connections:
                    elapsed = (now - conn.last_heartbeat).total_seconds()
                    if elapsed > timeout_seconds:
                        stale.append((user_id, conn.websocket))

        for user_id, ws in stale:
            try:
                await ws.close(code=1000, reason="心跳超时")
            except Exception:
                pass
            await self.disconnect(user_id, ws)

    async def start_cleanup_loop(self, interval: int = 60) -> None:
        """启动定时清理任务，每 interval 秒执行一次 cleanup_stale"""
        while True:
            await asyncio.sleep(interval)
            await self.cleanup_stale()


# 模块级单例实例
manager = ConnectionManager()
