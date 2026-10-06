"""调用运行中的服务器进行训练"""
import requests, sys

url = "http://127.0.0.1:7860/api/train"
status_url = "http://127.0.0.1:7860/api/status"

# 先检查服务器是否在运行
try:
    r = requests.get(status_url, timeout=5)
    print(f"服务器状态: {r.status_code}")
except Exception as e:
    print(f"无法连接服务器 (http://127.0.0.1:7860)")
    print(f"错误: {e}")
    print("请确认 start.bat 窗口已显示 'Uvicorn running on http://127.0.0.1:7860'")
    sys.exit(1)

# 发送训练请求
try:
    print("正在发送训练请求（训练约需 3-5 分钟）...")
    r = requests.post(url, timeout=600)
    print(f"结果: {r.json().get('result', 'OK')}")
except requests.exceptions.ConnectionError:
    print("训练请求失败: 连接断开")
    print("请确认服务器窗口仍然开着，并且没有报错")
    sys.exit(1)
except Exception as e:
    print(f"训练请求失败: {e}")
    sys.exit(1)
