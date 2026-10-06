"""
AI 自己：FastAPI 后端 + 流式输出
"""
import os
import sys
import base64
import json
import torch
import uvicorn
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TextIteratorStreamer
from peft import PeftModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from memory_module import MemoryModule
from config import *

app = FastAPI()

# ===== 素材加载 =====
_bg_data_uri = None
_avatar_data_uri = None


def load_assets():
    global _bg_data_uri, _avatar_data_uri
    bg = None
    avatar = None
    if os.path.isdir(ASSETS_DIR):
        for f in os.listdir(ASSETS_DIR):
            fpath = os.path.join(ASSETS_DIR, f)
            if not os.path.isfile(fpath): continue
            fl = f.lower()
            if avatar is None and ("avatar" in fl or "icon" in fl or "logo" in fl):
                avatar = fpath
            elif bg is None and ("bg" in fl or "back" in fl):
                bg = fpath
        if bg is None or avatar is None:
            for f in os.listdir(ASSETS_DIR):
                fpath = os.path.join(ASSETS_DIR, f)
                if not os.path.isfile(fpath): continue
                if bg is None:
                    bg = fpath
                elif avatar is None:
                    avatar = fpath
                    break
    if bg:
        with open(bg, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            ext = os.path.splitext(bg)[1].lower().lstrip(".")
            mime = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
            _bg_data_uri = f"data:{mime.get(ext, 'image/png')};base64,{b64}"
    if avatar:
        with open(avatar, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            ext = os.path.splitext(avatar)[1].lower().lstrip(".")
            mime = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
            _avatar_data_uri = f"data:{mime.get(ext, 'image/png')};base64,{b64}"


# ===== 模型引擎 =====
class BotEngine:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.memory = MemoryModule()
        self.load_model()

    def load_model(self):
        print("[加载] 加载 Qwen2.5-7B-Instruct (4-bit)...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH, trust_remote_code=True, padding_side="right",
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH, quantization_config=bnb_config, device_map="auto",
            trust_remote_code=True, dtype=torch.float16,
            attn_implementation="sdpa",
        )
        lora_path = LORA_OUTPUT_DIR
        if os.path.exists(os.path.join(lora_path, "adapter_config.json")):
            print(f"[加载] 加载 LoRA 权重: {lora_path}")
            self.model = PeftModel.from_pretrained(self.model, lora_path)
        print(f"[加载] 模型加载完成，显存: {torch.cuda.memory_allocated()/1024**3:.2f} GB")
        self.model.eval()

    def build_messages(self, message, history):
        memory_context = self.memory.format_memory_context(message)
        messages = []
        if memory_context:
            messages.append({"role": "system", "content": f"你是一个个人 AI 助手。\n\n以下是相关的历史记忆：\n{memory_context}\n\n请以自然的方式继续对话，如果记忆相关可以参考。"})
        else:
            messages.append({"role": "system", "content": "你是一个个人 AI 助手，了解我的背景、经历和性格特点。"})
        for h in history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})
        return messages

    def generate(self, message, history):
        messages = self.build_messages(message, history)
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, max_new_tokens=512, temperature=0.7, top_p=0.9,
                repetition_penalty=1.05, do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        reply = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        self.memory.add_memory(message, reply)
        return reply

    async def generate_stream(self, message, history):
        """流式生成，逐 token 产出"""
        messages = self.build_messages(message, history)
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        # TextIteratorStreamer 在独立线程中运行
        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=True,
            timeout=None,
        )
        gen_kwargs = dict(
            **inputs, max_new_tokens=512, temperature=0.7, top_p=0.9,
            repetition_penalty=1.05, do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
            streamer=streamer,
        )

        import threading
        thread = threading.Thread(target=self.model.generate, kwargs=gen_kwargs)
        thread.start()

        full_reply = ""
        for new_text in streamer:
            full_reply += new_text
            # SSE 格式：data: json\n\n
            yield f"data: {json.dumps({'token': new_text, 'full': full_reply})}\n\n"

        self.memory.add_memory(message, full_reply.strip())

    def get_status(self):
        cuda_ok = torch.cuda.is_available()
        if cuda_ok:
            gpu_name = torch.cuda.get_device_name(0)
            mem_used = torch.cuda.memory_allocated() / 1024**3
            mem_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            gpu_info = f"{gpu_name} | 显存: {mem_used:.1f}/{mem_total:.1f} GB"
        else:
            gpu_info = "CPU 模式"
        lora_loaded = "已加载" if os.path.exists(os.path.join(LORA_OUTPUT_DIR, "adapter_config.json")) else "未微调"
        return gpu_info, f"{gpu_info} | LoRA: {lora_loaded} | 记忆: {self.memory.get_memory_count()} 条", self.memory.get_today_summary()


bot = None


@app.get("/")
def index():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(html)


@app.get("/api/assets")
def api_assets():
    _, detail, memory = bot.get_status()
    return {
        "bg": _bg_data_uri or "",
        "avatar": _avatar_data_uri or "",
        "status": "运行中",
        "detail": detail,
        "memory": memory,
    }


@app.get("/api/status")
def api_status():
    _, detail, memory = bot.get_status()
    return {"status": "运行中", "detail": detail, "memory": memory}


@app.post("/api/clear")
def api_clear():
    _, _, memory = bot.get_status()
    return {"memory": memory}


# ===== 活动追踪（供桌面小宠使用） =====
import time
_last_activity = time.time()

@app.post("/api/chat")
async def api_chat(req: Request):
    global _last_activity
    _last_activity = time.time()
    data = await req.json()
    reply = bot.generate(data["message"], data["history"])
    return {"reply": reply}


@app.post("/api/chat/stream")
async def api_chat_stream(req: Request):
    global _last_activity
    _last_activity = time.time()
    data = await req.json()
    return StreamingResponse(
        bot.generate_stream(data["message"], data["history"]),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/activity")
def api_activity():
    """返回小宠需要的状态信息"""
    global _last_activity
    idle_seconds = time.time() - _last_activity
    status = "idle"
    if idle_seconds < 10:
        status = "chatting"  # 正在聊天
    elif idle_seconds < 120:
        status = "idle"      # 短时间空闲
    else:
        status = "sleep"     # 长时间空闲
    return {"status": status, "idle_seconds": int(idle_seconds)}


if __name__ == "__main__":
    import sys
    load_assets()
    bot = BotEngine()
    uvicorn.run(app, host="127.0.0.1", port=7860, log_level="info")
