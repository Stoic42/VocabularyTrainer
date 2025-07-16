#!/usr/bin/env python3
"""
TTS超时保护测试脚本
用于验证TTS音频生成是否会在超时时正确处理
"""

import requests
import time
import json

def test_tts_timeout():
    """测试TTS超时保护"""
    base_url = "http://localhost:8000"
    
    # 测试正常TTS请求
    print("1. 测试正常TTS请求...")
    try:
        response = requests.get(f"{base_url}/api/tts/test", timeout=35)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 正常TTS请求成功")
        else:
            print(f"   ❌ 正常TTS请求失败: {response.text}")
    except requests.exceptions.Timeout:
        print("   ❌ 正常TTS请求超时")
    except Exception as e:
        print(f"   ❌ 正常TTS请求异常: {e}")
    
    # 测试多个并发TTS请求
    print("\n2. 测试并发TTS请求...")
    words = ["hello", "world", "test", "timeout", "protection"]
    start_time = time.time()
    
    for i, word in enumerate(words):
        try:
            print(f"   请求 {i+1}: /api/tts/{word}")
            response = requests.get(f"{base_url}/api/tts/{word}", timeout=35)
            print(f"   状态码: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"   ❌ 请求 {i+1} 超时")
        except Exception as e:
            print(f"   ❌ 请求 {i+1} 异常: {e}")
    
    end_time = time.time()
    print(f"   总耗时: {end_time - start_time:.2f}秒")
    
    # 测试服务器状态
    print("\n3. 测试服务器状态...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   主页状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 服务器正常运行")
        else:
            print("   ❌ 服务器异常")
    except Exception as e:
        print(f"   ❌ 服务器连接失败: {e}")

if __name__ == "__main__":
    print("开始TTS超时保护测试...\n")
    test_tts_timeout()
    print("\n测试完成！") 