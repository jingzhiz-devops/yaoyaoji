#!/usr/bin/env python3
"""
验证 AI 医生模块改进是否已正确应用
"""

import os
import re
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (不存在)")
        return False

def check_code_exists(file_path, code_pattern, description):
    """检查代码是否存在"""
    if not os.path.exists(file_path):
        print(f"❌ {description}: 文件不存在")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if re.search(code_pattern, content, re.DOTALL):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description}")
        return False

def main():
    """主验证程序"""
    print("=" * 70)
    print("🔍 验证 AI 医生模块改进")
    print("=" * 70)
    print()
    
    project_root = Path(__file__).parent
    results = {}
    
    # 检查 1: 核心代码文件
    print("📋 检查 1: 核心代码文件")
    print("-" * 70)
    
    ai_doctor_file = project_root / 'app' / 'routers' / 'ai_doctor.py'
    results['ai_doctor_file'] = check_file_exists(
        ai_doctor_file,
        "ai_doctor.py"
    )
    print()
    
    # 检查 2: 代码改进
    print("📋 检查 2: 代码改进")
    print("-" * 70)
    
    checks = [
        (
            ai_doctor_file,
            r'def create_deepseek_client\(timeout: float = 60\.0\)',
            "create_deepseek_client() 函数"
        ),
        (
            ai_doctor_file,
            r'def call_deepseek_api\(',
            "call_deepseek_api() 函数"
        ),
        (
            ai_doctor_file,
            r'timeout=60\.0',
            "60 秒超时配置"
        ),
        (
            ai_doctor_file,
            r'max_retries: int = 2',
            "2 次重试机制"
        ),
        (
            ai_doctor_file,
            r'http2=False',
            "HTTP/2 禁用（兼容性优化）"
        ),
        (
            ai_doctor_file,
            r'verify=True',
            "SSL 证书验证"
        ),
        (
            ai_doctor_file,
            r'follow_redirects=True',
            "重定向跟随"
        ),
        (
            ai_doctor_file,
            r'create_deepseek_client\(timeout=60\.0\)',
            "/predict 端点使用新客户端创建函数"
        ),
        (
            ai_doctor_file,
            r'call_deepseek_api\(',
            "使用 call_deepseek_api 进行 API 调用"
        ),
    ]
    
    for file_path, pattern, desc in checks:
        results[desc] = check_code_exists(file_path, pattern, desc)
    
    print()
    
    # 检查 3: 诊断工具
    print("📋 检查 3: 诊断工具")
    print("-" * 70)
    
    test_files = [
        (
            project_root / 'test_deepseek_connection.py',
            "完整诊断脚本"
        ),
        (
            project_root / 'quick_test_api.py',
            "快速测试脚本"
        ),
    ]
    
    for file_path, desc in test_files:
        results[f'{desc}'] = check_file_exists(file_path, desc)
    
    print()
    
    # 检查 4: 文档
    print("📋 检查 4: 文档")
    print("-" * 70)
    
    doc_files = [
        (
            project_root.parent / 'DEEPSEEK_QUICK_START.md',
            "快速开始指南"
        ),
        (
            project_root.parent / 'DEEPSEEK_CONNECTION_FIX.md',
            "详细修复指南"
        ),
        (
            project_root.parent / 'AI_DOCTOR_IMPROVEMENTS.md',
            "改进总结文档"
        ),
    ]
    
    for file_path, desc in doc_files:
        results[f'{desc}'] = check_file_exists(file_path, desc)
    
    print()
    
    # 检查 5: 代码语法
    print("📋 检查 5: 代码语法")
    print("-" * 70)
    
    try:
        import py_compile
        py_compile.compile(str(ai_doctor_file), doraise=True)
        print("✅ ai_doctor.py 语法正确")
        results['语法检查'] = True
    except py_compile.PyCompileError as e:
        print(f"❌ ai_doctor.py 语法错误: {e}")
        results['语法检查'] = False
    
    print()
    
    # 生成总结
    print("=" * 70)
    print("📊 验证总结")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"通过: {passed}/{total} ({percentage:.1f}%)")
    print()
    
    if passed == total:
        print("✅ 所有检查都通过了！改进已成功应用。")
        print()
        print("下一步:")
        print("1. 启动应用: python -m app.main")
        print("2. 运行快速测试: python quick_test_api.py")
        print("3. 查看文档: cat ../DEEPSEEK_QUICK_START.md")
        return 0
    else:
        print("❌ 有些检查未通过，请检查上面的错误信息。")
        failed = [k for k, v in results.items() if not v]
        print()
        print("失败的检查:")
        for item in failed:
            print(f"  - {item}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
