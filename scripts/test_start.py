"""Test: start server, wait, test APIs, then start training"""
import sys, os, time, threading, requests

sys.path = ['D:/ai_self/chat_interface', 'D:/ai_self'] + sys.path
os.chdir('D:/ai_self')

import uvicorn
from app import app, load_assets, BotEngine, bot as bot_module

print("[1] Loading model...")
load_assets()
server_bot = BotEngine()

# Set module-level bot
import app as app_mod
app_mod.bot = server_bot

print("[2] Starting server...")
server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=7860, log_level="warning"))
thread = threading.Thread(target=server.run)
thread.start()

time.sleep(3)

print("[3] Testing API...")
for ep in ["/", "/api/status", "/api/assets"]:
    try:
        r = requests.get(f"http://127.0.0.1:7860{ep}", timeout=5)
        print(f"  {ep}: {r.status_code}")
    except Exception as e:
        print(f"  {ep}: FAILED - {e}")

print("[4] Starting training...")
try:
    r = requests.post("http://127.0.0.1:7860/api/train", timeout=600)
    print(f"  Train result: {r.json()}")
except Exception as e:
    print(f"  Train FAILED: {e}")

print("[5] Done")
server.should_exit = True
thread.join(timeout=5)
