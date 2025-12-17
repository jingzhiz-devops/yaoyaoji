#!/usr/bin/env python3
"""
快速测试 DeepSeek API 连接脚本
"""
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(project_root / '.env')

print("=" * 60)
print("🚀 DeepSeek API 快速连接测试")
print("=" * 60)

try:
    from openai import OpenAI
    import httpx
    print("✅ 导入库成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

api_key = os.getenv('DEEPSEEK_API_KEY')
base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')

if not api_key:
    print("❌ 错误: DEEPSEEK_API_KEY 未设置")
    sys.exit(1)

print(f"✅ API Key: {api_key[:10]}...{api_key[-5:]}")
print(f"✅ Base URL: {base_url}")
print()

print("正在创建客户端...")
try:
    http_client = httpx.Client(
        timeout=60.0,
        limits=httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10,
            keepalive_expiry=30.0
        ),
        verify=True,
        follow_redirects=True,
        http2=False
    )
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=http_client
    )
    print("✅ 客户端创建成功")
except Exception as e:
    print(f"❌ 客户端创建失败: {e}")
    sys.exit(1)

print()
print("正在调用 API 测试...")
print("-" * 60)

try:
    print("发送测试请求...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "请简要确认你收到了这条消息。"}
        ],
        temperature=0.3,
        max_tokens=50,
        stream=False
    )
    
    ai_response = response.choices[0].message.content
    print(f"✅ 收到响应: {ai_response}")
    print()
    print("=" * 60)
    print("✅ 所有测试通过！DeepSeek API 连接正常。")
    print("=" * 60)
    
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e)
    
    print(f"❌ API 调用失败: {error_type}: {error_msg}")
    print()
    print("=" * 60)
    print("❌ DeepSeek API 连接失败")
    print("=" * 60)
    print()
    print("建议:")
    if "401" in error_msg or "Unauthorized" in error_msg:
        print("- API Key 无效或已过期")
        print("- 访问 https://platform.deepseek.com/api_keys 检查")
    elif "Connection" in error_type:
        print("- 网络连接问题")
        print("- 检查防火墙和代理设置")
    elif "Timeout" in error_type:
        print("- 请求超时")
        print("- 可能是网络延迟或 API 服务响应缓慢")
    
    sys.exit(1)

http_client.close()
