"""
图形验证码模块 — 基于内存存储，适合单实例部署
"""
import random
import string
import time
import uuid
from io import BytesIO
from captcha.image import ImageCaptcha

# 内存存储: {captcha_id: (code, expire_time)}
_captcha_store: dict[str, tuple[str, float]] = {}

# 验证码有效期（秒）
CAPTCHA_EXPIRE = 300  # 5 分钟
# 验证码字符长度
CAPTCHA_LENGTH = 4
# 定期清理阈值
_CLEANUP_THRESHOLD = 500


def _cleanup_expired():
    """清理过期验证码，防止内存泄漏"""
    now = time.time()
    expired = [k for k, (_, exp) in _captcha_store.items() if now > exp]
    for k in expired:
        del _captcha_store[k]


def generate_captcha() -> tuple[str, bytes]:
    """
    生成验证码图片。
    返回 (captcha_id, image_bytes)
    """
    if len(_captcha_store) > _CLEANUP_THRESHOLD:
        _cleanup_expired()

    # 生成随机字符（排除容易混淆的字符）
    chars = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '').replace('1', '')
    code = ''.join(random.choices(chars, k=CAPTCHA_LENGTH))

    # 生成图片
    image = ImageCaptcha(width=160, height=60)
    data: BytesIO = image.generate(code)

    # 存储
    captcha_id = uuid.uuid4().hex
    _captcha_store[captcha_id] = (code.upper(), time.time() + CAPTCHA_EXPIRE)

    return captcha_id, data.getvalue()


def verify_captcha(captcha_id: str, code: str) -> bool:
    """
    验证验证码，验证后立即删除（一次性使用）。
    """
    _cleanup_expired()

    entry = _captcha_store.pop(captcha_id, None)
    if entry is None:
        return False

    stored_code, expire_time = entry
    if time.time() > expire_time:
        return False

    return code.strip().upper() == stored_code
