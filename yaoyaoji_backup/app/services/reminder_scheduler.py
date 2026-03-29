"""
用药提醒调度器

后台定时任务，每分钟检查一次是否有需要触发的用药提醒，
如果匹配当前时间和星期，则通过飞书发送通知。
支持用户级别的 Webhook 和系统级别的私聊两种模式。
"""
import asyncio
import logging
from datetime import datetime, time as time_type
import httpx

from app.database import SessionLocal
from app.models.models import MedicationReminder, ReminderStatus, User, ChronicDisease, UserMedication
from app.services.feishu import send_medication_reminder

logger = logging.getLogger(__name__)

# 记录已发送的提醒，避免同一分钟重复发送  key: f"{reminder_id}:{date}:{HH:MM}"
_sent_cache: set[str] = set()
_MAX_CACHE_SIZE = 5000


def _cleanup_cache():
    """缓存过大时清理。"""
    global _sent_cache
    if len(_sent_cache) > _MAX_CACHE_SIZE:
        _sent_cache = set()


async def send_webhook_notification(webhook_url: str, username: str, medicine_name: str, reminder_time: str, notes: str = "") -> bool:
    """通过用户 Webhook 发送飞书通知"""
    try:
        elements = [
            {"tag": "div", "fields": [
                {"is_short": True, "text": {"tag": "lark_md", "content": f"**💊 药品**\n{medicine_name}"}},
                {"is_short": True, "text": {"tag": "lark_md", "content": f"**⏰ 时间**\n{reminder_time}"}},
            ]},
        ]
        
        if notes:
            elements.append({"tag": "div", "fields": [
                {"is_short": False, "text": {"tag": "lark_md", "content": f"**📝 备注**\n{notes}"}},
            ]})
        
        elements.append({"tag": "hr"})
        elements.append({"tag": "note", "elements": [{"tag": "plain_text", "content": "来自「药药记」智能用药管理系统"}]})
        
        card = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": "💊 用药提醒"},
                    "template": "turquoise",
                },
                "elements": elements,
            }
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json=card)
            result = resp.json()
            return result.get("StatusCode") == 0 or result.get("code") == 0
    except Exception as e:
        logger.error("Webhook 发送失败: %s", e)
        return False


async def check_and_send_reminders():
    """检查当前时刻是否有需要触发的提醒，并发送飞书通知。"""
    now = datetime.now()
    current_time = now.time().replace(second=0, microsecond=0)
    current_weekday = now.isoweekday()  # 1=周一 ... 7=周日
    today_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    db = SessionLocal()
    try:
        reminders = db.query(MedicationReminder).filter(
            MedicationReminder.status == ReminderStatus.ACTIVE
        ).all()

        for r in reminders:
            # 检查星期是否匹配
            days = r.reminder_days or []
            if current_weekday not in days:
                continue

            # 检查时间是否匹配（精确到分钟）
            reminder_hm = r.reminder_time.strftime("%H:%M") if isinstance(r.reminder_time, time_type) else str(r.reminder_time)[:5]
            if reminder_hm != time_str:
                continue

            # 去重
            cache_key = f"{r.id}:{today_str}:{time_str}"
            if cache_key in _sent_cache:
                continue

            # 查询关联信息
            user = db.query(User).filter(User.id == r.user_id).first()
            disease = db.query(ChronicDisease).filter(ChronicDisease.id == r.disease_id).first()
            med_name = "未指定药品"
            notes = ""
            if r.user_medication_id:
                user_med = db.query(UserMedication).filter(UserMedication.id == r.user_medication_id).first()
                if user_med and user_med.medicine:
                    med_name = user_med.medicine.name
                elif user_med and user_med.custom_name:
                    med_name = user_med.custom_name
                if user_med:
                    notes = user_med.notes or ""

            username = user.username if user else "未知用户"

            if not user:
                logger.debug("用户不存在，跳过通知")
                continue

            # 优先使用用户配置的 Webhook
            if user.feishu_webhook:
                ok = await send_webhook_notification(
                    user.feishu_webhook,
                    username,
                    med_name,
                    reminder_hm,
                    notes
                )
                if ok:
                    _sent_cache.add(cache_key)
                    logger.info("飞书Webhook提醒已发送: user=%s, med=%s, time=%s", username, med_name, reminder_hm)
                else:
                    logger.warning("飞书Webhook提醒发送失败: reminder_id=%s", r.id)
            else:
                # 回退到系统私聊模式（需要手机号/邮箱）
                if not user.phone and not user.email:
                    logger.debug("用户 %s 无飞书Webhook且无手机号/邮箱，跳过通知", username)
                    continue
                
                ok = await send_medication_reminder(
                    username=username,
                    medicine_name=med_name,
                    reminder_time=reminder_hm,
                    notes=notes,
                    phone=user.phone,
                    email=user.email,
                )
                if ok:
                    _sent_cache.add(cache_key)
                    logger.info("飞书私聊提醒已发送: user=%s, med=%s, time=%s", username, med_name, reminder_hm)
                else:
                    logger.warning("飞书私聊提醒发送失败: reminder_id=%s", r.id)

    except Exception as e:
        logger.error("提醒检查异常: %s", e)
    finally:
        db.close()
        _cleanup_cache()


async def start_reminder_loop(interval: int = 60):
    """启动提醒检查循环，默认每 60 秒检查一次。"""
    logger.info("用药提醒调度器已启动 (间隔 %ds)", interval)
    while True:
        await check_and_send_reminders()
        await asyncio.sleep(interval)
