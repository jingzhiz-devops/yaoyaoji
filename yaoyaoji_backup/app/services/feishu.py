"""
飞书通知服务

通过飞书自建应用直接给用户发私聊消息。
根据用户手机号或邮箱查找飞书 open_id，然后发送卡片消息。
需要在飞书开放平台为应用开启：
  - contact:user.phone:readonly（通过手机号查用户）
  - im:message:send_as_bot（发送消息）
"""
import json
import time
import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
FEISHU_MESSAGE_URL = "https://open.feishu.cn/open-apis/im/v1/messages"
FEISHU_USER_BATCH_URL = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"

_token_cache: dict = {"token": "", "expire_at": 0}
# 手机号/邮箱 → open_id 缓存
_user_id_cache: dict[str, str] = {}


async def _get_tenant_access_token() -> str:
    """获取 tenant_access_token，带本地缓存。"""
    now = time.time()
    if _token_cache["token"] and _token_cache["expire_at"] > now + 60:
        return _token_cache["token"]

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(FEISHU_TOKEN_URL, json={
            "app_id": settings.FEISHU_APP_ID,
            "app_secret": settings.FEISHU_APP_SECRET,
        })
        data = resp.json()

    if data.get("code") != 0:
        logger.error("获取飞书 token 失败: %s", data)
        raise RuntimeError(f"飞书 token 获取失败: {data.get('msg')}")

    _token_cache["token"] = data["tenant_access_token"]
    _token_cache["expire_at"] = now + data.get("expire", 7200)
    return _token_cache["token"]


async def get_open_id_by_phone(phone: str) -> str | None:
    """通过手机号查找飞书用户 open_id。"""
    if phone in _user_id_cache:
        return _user_id_cache[phone]

    try:
        token = await _get_tenant_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                FEISHU_USER_BATCH_URL,
                headers=headers,
                params={"user_id_type": "open_id"},
                json={"mobiles": [phone]},
            )
            data = resp.json()

        if data.get("code") != 0:
            logger.error("飞书查找用户失败: %s", data)
            return None

        user_list = data.get("data", {}).get("user_list", [])
        if user_list and user_list[0].get("user_id"):
            open_id = user_list[0]["user_id"]
            _user_id_cache[phone] = open_id
            return open_id

        logger.warning("飞书未找到手机号 %s 对应的用户", phone)
        return None
    except Exception as e:
        logger.error("查找飞书用户异常: %s", e)
        return None


async def get_open_id_by_email(email: str) -> str | None:
    """通过邮箱查找飞书用户 open_id。"""
    if email in _user_id_cache:
        return _user_id_cache[email]

    try:
        token = await _get_tenant_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                FEISHU_USER_BATCH_URL,
                headers=headers,
                params={"user_id_type": "open_id"},
                json={"emails": [email]},
            )
            data = resp.json()

        if data.get("code") != 0:
            logger.error("飞书查找用户失败: %s", data)
            return None

        user_list = data.get("data", {}).get("user_list", [])
        if user_list and user_list[0].get("user_id"):
            open_id = user_list[0]["user_id"]
            _user_id_cache[email] = open_id
            return open_id

        return None
    except Exception as e:
        logger.error("查找飞书用户异常: %s", e)
        return None


async def resolve_open_id(phone: str | None, email: str | None) -> str | None:
    """优先用手机号查，查不到再用邮箱查。"""
    if phone:
        oid = await get_open_id_by_phone(phone)
        if oid:
            return oid
    if email:
        oid = await get_open_id_by_email(email)
        if oid:
            return oid
    return None


async def send_feishu_message(open_id: str, content: dict, msg_type: str = "interactive") -> bool:
    """向指定用户发送私聊消息。"""
    try:
        token = await _get_tenant_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "receive_id": open_id,
            "msg_type": msg_type,
            "content": json.dumps(content) if isinstance(content, dict) else content,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                FEISHU_MESSAGE_URL,
                params={"receive_id_type": "open_id"},
                headers=headers,
                json=payload,
            )
            result = resp.json()

        if result.get("code") != 0:
            logger.error("飞书消息发送失败: %s", result)
            return False

        logger.info("飞书私聊消息发送成功: open_id=%s", open_id)
        return True
    except Exception as e:
        logger.error("飞书消息发送异常: %s", e)
        return False


def build_reminder_card(username: str, medicine_name: str, reminder_time: str, notes: str = "") -> dict:
    """构建用药提醒卡片消息。"""
    elements = [
        {
            "tag": "div",
            "fields": [
                {"is_short": True, "text": {"tag": "lark_md", "content": f"**💊 药品**\n{medicine_name}"}},
                {"is_short": True, "text": {"tag": "lark_md", "content": f"**⏰ 时间**\n{reminder_time}"}},
            ],
        },
    ]
    
    # 添加备注（如果有）
    if notes:
        elements.append({
            "tag": "div",
            "fields": [
                {"is_short": False, "text": {"tag": "lark_md", "content": f"**📝 备注**\n{notes}"}},
            ],
        })
    
    elements.append({"tag": "hr"})
    elements.append({
        "tag": "note",
        "elements": [{"tag": "plain_text", "content": "来自「药药记」智能用药管理系统"}],
    })
    
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "💊 用药提醒"},
            "template": "turquoise",
        },
        "elements": elements,
    }


async def send_medication_reminder(
    username: str,
    medicine_name: str,
    reminder_time: str,
    notes: str = "",
    phone: str | None = None,
    email: str | None = None,
) -> bool:
    """发送用药提醒私聊消息。通过手机号或邮箱找到飞书用户后直接发。"""
    open_id = await resolve_open_id(phone, email)
    if not open_id:
        logger.warning("无法找到飞书用户: phone=%s, email=%s，跳过通知", phone, email)
        return False

    card = build_reminder_card(username, medicine_name, reminder_time, notes)
    return await send_feishu_message(open_id, card, msg_type="interactive")


def is_feishu_configured() -> bool:
    """检查飞书配置是否完整（只需要 App ID 和 Secret）。"""
    return bool(settings.FEISHU_APP_ID and settings.FEISHU_APP_SECRET)
