#!/usr/bin/env python3
"""诊断脚本 - 检查 NL2SQL 系统连接"""

import requests
import sys
import json
from urllib.parse import urljoin

# 颜色输出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

API_URL = "http://localhost:8000"

def print_status(status: bool, message: str):
    """打印状态消息"""
    icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{icon} {message}")

def test_backend_connection():
    """测试后端连接"""
    print(f"\n{YELLOW}测试后端连接:{RESET}")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print_status(True, f"后端服务运行中 (端口 8000)")
            print(f"  响应: {response.json()}")
            return True
        else:
            print_status(False, f"后端响应错误: {response.status_code}")
            return False
    except requests.ConnectionError:
        print_status(False, "无法连接到后端服务 - 请确保 8000 端口已启动")
        print(f"  运行: uv run uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print_status(False, f"连接错误: {e}")
        return False

def test_cors():
    """测试 CORS 配置"""
    print(f"\n{YELLOW}测试 CORS 配置:{RESET}")
    try:
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
        response = requests.options(f"{API_URL}/api/chat", headers=headers, timeout=5)
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
        }
        
        if cors_headers["Access-Control-Allow-Origin"]:
            print_status(True, "CORS 已正确配置")
            for key, value in cors_headers.items():
                if value:
                    print(f"  {key}: {value}")
            return True
        else:
            print_status(False, "CORS 未返回预期的头部")
            return False
    except Exception as e:
        print_status(False, f"CORS 测试失败: {e}")
        return False

def test_chat_api():
    """测试聊天 API"""
    print(f"\n{YELLOW}测试聊天 API:{RESET}")
    try:
        payload = {
            "question": "测试问题"
        }
        response = requests.post(
            f"{API_URL}/api/chat",
            json=payload,
            timeout=15,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"  响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print_status(True, "聊天 API 工作正常")
            data = response.json()
            print(f"  SQL 查询已生成 ({len(data.get('sql', ''))} 字符)")
            return True
        elif response.status_code == 400:
            print_status(False, f"请求错误: {response.text}")
            return False
        elif response.status_code == 401:
            print_status(False, f"认证失败: {response.text}")
            print(f"  💡 提示: 请检查 backend/.env 中的 ARK_API_KEY 是否正确")
            print(f"  📣 查看详情: API_KEY_SETUP.md")
            return False
        elif response.status_code == 503:
            print_status(False, f"服务无法初始化: {response.text}")
            print(f"  💡 提示: 这通常意味着 API 密钥配置有问题")
            print(f"  📣 查看详情: API_KEY_SETUP.md")
            return False
        elif response.status_code == 500:
            print_status(False, f"服务器错误: {response.text}")
            return False
        else:
            print_status(False, f"未预期的响应: {response.status_code}")
            try:
                print(f"  响应内容: {response.json()}")
            except:
                print(f"  响应内容: {response.text[:200]}")
            return False
    except requests.Timeout:
        print_status(False, "请求超时 - LLM API 响应缓慢或无响应")
        print("  检查事项:")
        print("    - ARK_API_KEY 是否正确设置")
        print("    - ARK_BASE_URL 是否可访问")
        print("    - 网络连接是否正常")
        return False
    except Exception as e:
        print_status(False, f"API 测试失败: {e}")
        return False

def test_tables_api():
    """测试表 API"""
    print(f"\n{YELLOW}测试表结构 API:{RESET}")
    try:
        response = requests.get(f"{API_URL}/api/tables", timeout=5)
        if response.status_code == 200:
            tables = response.json()
            print_status(True, f"表结构加载成功 ({len(tables)} 个表)")
            for table_name in list(tables.keys())[:3]:
                print(f"  - {table_name}")
            return True
        else:
            print_status(False, f"获取表结构失败: {response.status_code}")
            return False
    except Exception as e:
        print_status(False, f"表 API 测试失败: {e}")
        return False

def main():
    """运行所有诊断"""
    print(f"\n{YELLOW}{'='*50}{RESET}")
    print(f"{YELLOW}NL2SQL 系统诊断{RESET}")
    print(f"{YELLOW}{'='*50}{RESET}\n")
    
    results = []
    
    # 测试后端连接
    backend_ok = test_backend_connection()
    results.append(("后端连接", backend_ok))
    
    if backend_ok:
        # 测试 CORS
        cors_ok = test_cors()
        results.append(("CORS 配置", cors_ok))
        
        # 测试表 API
        tables_ok = test_tables_api()
        results.append(("表结构 API", tables_ok))
        
        # 测试聊天 API
        chat_ok = test_chat_api()
        results.append(("聊天 API", chat_ok))
    
    # 总结
    print(f"\n{YELLOW}{'='*50}{RESET}")
    print(f"{YELLOW}诊断总结:{RESET}")
    print(f"{YELLOW}{'='*50}{RESET}\n")
    
    for test_name, passed in results:
        print_status(passed, test_name)
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print(f"\n{GREEN}✓ 所有测试通过! 系统可以正常使用.{RESET}")
        return 0
    else:
        print(f"\n{RED}✗ 部分测试失败，请查看上面的错误信息.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
