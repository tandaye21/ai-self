"""生成 index.html（确保中文 UTF-8 编码正确）"""
import os, base64

ASSETS_DIR = r"C:\Users\田永杰\Desktop\图片与音频素材\页面图片"

def img_to_data_uri(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
    return f"data:{mime.get(ext, 'image/png')};base64,{b64}"

# 加载图片：OIP-C (2) 作为 AI 头像，OIP-C (3) 作为用户头像
# OIP-C (1) 作为聊天背景
bg_uri = None
bot_av_uri = None
user_av_uri = None
if os.path.isdir(ASSETS_DIR):
    for f in sorted(os.listdir(ASSETS_DIR)):
        fp = os.path.join(ASSETS_DIR, f)
        if not os.path.isfile(fp): continue
        fl = f.lower()
        if "(2)" in fl and "oip" in fl:
            bot_av_uri = img_to_data_uri(fp)
        elif "(3)" in fl and "oip" in fl:
            user_av_uri = img_to_data_uri(fp)
        elif "(1)" in fl and "oip" in fl:
            bg_uri = img_to_data_uri(fp)
    # fallback
    if bot_av_uri is None:
        for f in sorted(os.listdir(ASSETS_DIR)):
            fp = os.path.join(ASSETS_DIR, f)
            if not os.path.isfile(fp): continue
            if fp != bg_uri and fp != user_av_uri:
                bot_av_uri = img_to_data_uri(fp)
                break
    if user_av_uri is None:
        for f in sorted(os.listdir(ASSETS_DIR)):
            fp = os.path.join(ASSETS_DIR, f)
            if not os.path.isfile(fp): continue
            if fp != bg_uri and fp != bot_av_uri:
                user_av_uri = img_to_data_uri(fp)
                break

bot_av_style = f'style="background-image:url({bot_av_uri});background-size:cover;background-position:center"' if bot_av_uri else 'class="msg-avatar placeholder"'
bot_av_url_js = bot_av_uri or ""
user_av_url_js = user_av_uri or ""
bg_css = f"background-image:url({bg_uri});" if bg_uri else ""

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>分身 - 芙莉莲</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{
    font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;
    background:linear-gradient(135deg,#e8d8f0 0%,#f0e0ee 50%,#e4d0ec 100%);
    min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;
}}
.chat-container{{
    width:100%;max-width:1100px;height:calc(100vh - 32px);
    background:rgba(255,255,255,0.65);
    backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
    border-radius:24px;border:1px solid rgba(255,255,255,0.6);
    box-shadow:0 8px 48px rgba(160,120,180,0.12);
    display:flex;flex-direction:column;overflow:hidden;position:relative;
}}
.chat-container::before{{
    content:'';position:absolute;inset:0;
    {bg_css}opacity:0.14;z-index:0;pointer-events:none;background-size:cover;background-position:center;
}}
.header{{
    padding:16px 24px;background:rgba(255,255,255,0.5);
    border-bottom:1px solid rgba(200,180,210,0.2);
    display:flex;align-items:center;gap:14px;position:relative;z-index:1;
}}
.header-avatar{{
    width:44px;height:44px;border-radius:50%;flex-shrink:0;
    border:2px solid rgba(200,180,210,0.3);
    background-size:cover;background-position:center;
}}
.header-avatar.placeholder{{background:linear-gradient(135deg,#b088c8,#d4a848)}}
.header-info{{flex:1;min-width:0}}
.header-title{{
    font-size:1.2em;font-weight:700;
    color:#5a4a6a;
}}
.header-sub{{font-size:0.78em;color:#9a8aaa;margin-top:1px}}
.header-status{{font-size:0.72em;color:#aaa0b0;text-align:right}}
.main{{flex:1;display:flex;overflow:hidden;position:relative;z-index:1}}
.chat-area{{flex:1;display:flex;flex-direction:column;min-width:0}}
.messages{{
    flex:1;overflow-y:auto;padding:16px 20px;
    display:flex;flex-direction:column;gap:10px;
}}
.messages::-webkit-scrollbar{{width:4px}}
.messages::-webkit-scrollbar-thumb{{background:rgba(160,120,180,0.15);border-radius:2px}}
.msg{{display:flex;gap:8px;max-width:85%;animation:fadeIn 0.3s ease}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
.msg.user{{align-self:flex-end;flex-direction:row-reverse}}
.msg.bot{{align-self:flex-start}}
.msg-avatar{{width:30px;height:30px;border-radius:50%;flex-shrink:0;background-size:cover;background-position:center;border:1px solid rgba(200,180,210,0.2)}}
.msg-avatar.placeholder{{background:linear-gradient(135deg,#b088c8,#d4a848)}}
.msg-bubble{{padding:10px 14px;border-radius:14px;font-size:0.9em;line-height:1.55;color:#4a3a5a}}
.msg.user .msg-bubble{{background:linear-gradient(135deg,#b088c8,#9a70b8);color:white;border-bottom-right-radius:4px}}
.msg.bot .msg-bubble{{background:white;border:1px solid rgba(200,180,210,0.25);border-bottom-left-radius:4px}}
.msg-time{{font-size:0.62em;color:#b0a0b8;margin-top:3px}}
.msg.user .msg-time{{text-align:right}}
.input-area{{padding:12px 20px 16px;border-top:1px solid rgba(200,180,210,0.15);background:rgba(255,255,255,0.3)}}
.input-row{{display:flex;gap:8px}}
.input-row textarea{{
    flex:1;padding:10px 14px;border-radius:12px;
    border:1px solid rgba(200,180,210,0.25);background:white;
    color:#4a3a5a;font-size:0.88em;font-family:inherit;resize:none;outline:none;
    transition:border 0.2s;line-height:1.4;
}}
.input-row textarea:focus{{border-color:#b088c8;box-shadow:0 0 0 2px rgba(176,136,200,0.1)}}
.input-row textarea::placeholder{{color:#b0a0b8}}
.btn-send{{
    padding:10px 24px;border-radius:12px;border:none;
    background:linear-gradient(135deg,#b088c8,#9a70b8);
    color:white;font-weight:600;font-size:0.85em;
    cursor:pointer;transition:all 0.2s;white-space:nowrap;
}}
.btn-send:hover{{transform:translateY(-1px);box-shadow:0 4px 16px rgba(176,136,200,0.25)}}
.sidebar{{width:200px;padding:16px;border-left:1px solid rgba(200,180,210,0.15);display:flex;flex-direction:column;gap:12px;background:rgba(255,255,255,0.15)}}
.sidebar-card{{background:rgba(255,255,255,0.5);border-radius:12px;padding:12px;border:1px solid rgba(200,180,210,0.15)}}
.sidebar-card-title{{font-size:0.7em;font-weight:600;color:#b088c8;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}}
.sidebar-card-content{{font-size:0.75em;color:#7a6a8a;line-height:1.5;white-space:pre-wrap;word-break:break-all;max-height:100px;overflow-y:auto}}
.sidebar-card-content::-webkit-scrollbar{{width:3px}}
.sidebar-card-content::-webkit-scrollbar-thumb{{background:rgba(160,120,180,0.1);border-radius:2px}}
.quick-tips{{list-style:none;padding:0}}
.quick-tips li{{padding:5px 0;font-size:0.75em;color:#8a7a9a;cursor:pointer;transition:color 0.2s;border-bottom:1px solid rgba(200,180,210,0.1)}}
.quick-tips li:hover{{color:#5a4a6a}}
.quick-tips li::before{{content:'✦ ';color:#b088c8}}
.btn-clear{{padding:6px;border-radius:8px;border:1px solid rgba(200,180,210,0.15);background:rgba(255,255,255,0.3);color:#9a8aaa;cursor:pointer;font-size:0.75em;transition:all 0.2s}}
.btn-clear:hover{{background:rgba(255,255,255,0.5);color:#5a4a6a}}
@media(max-width:768px){{.sidebar{{display:none}}.chat-container{{height:100vh;border-radius:0}}body{{padding:0}}}}
</style>
</head>
<body>
<div class="chat-container" id="app">
    <div class="header">
        <div class="header-avatar" {bot_av_style}></div>
        <div class="header-info">
            <div class="header-title">分身</div>
            <div class="header-sub">芙莉莲 · 记忆之旅</div>
        </div>
        <div class="header-status" id="statusText">加载中...</div>
    </div>
    <div class="main">
        <div class="chat-area">
            <div class="messages" id="messageList">
                <div class="msg bot">
                    <div class="msg-avatar" {bot_av_style}></div>
                    <div>
                        <div class="msg-bubble">你好，我是你的另一半。今天想聊点什么？</div>
                        <div class="msg-time">现在</div>
                    </div>
                </div>
            </div>
            <div class="input-area">
                <div class="input-row">
                    <textarea id="msgInput" rows="1" placeholder="输入你想说的话..." onkeydown="if(event.key=='Enter'&&!event.shiftKey){{event.preventDefault();sendMsg()}}"></textarea>
                    <button class="btn-send" onclick="sendMsg()">发送</button>
                </div>
            </div>
        </div>
        <div class="sidebar">
            <div class="sidebar-card">
                <div class="sidebar-card-title">📊 系统状态</div>
                <div class="sidebar-card-content" id="statusPanel">加载中...</div>
            </div>
            <div class="sidebar-card">
                <div class="sidebar-card-title">📝 今日记忆</div>
                <div class="sidebar-card-content" id="memoryPanel">加载中...</div>
            </div>
            <div class="sidebar-card" style="flex:1">
                <div class="sidebar-card-title">💡 快速开始</div>
                <ul class="quick-tips">
                    <li onclick="fillMsg('介绍一下你自己')">介绍你自己</li>
                    <li onclick="fillMsg('你有什么项目经历？')">你的项目经历</li>
                    <li onclick="fillMsg('你是个什么样的人？')">你是什么样的人</li>
                    <li onclick="fillMsg('今天有什么想说的？')">随便聊聊</li>
                </ul>
            </div>
            <button class="btn-clear" onclick="clearChat()">清空对话</button>
        </div>
    </div>
</div>
<script>
const BOT_AVATAR = "{bot_av_url_js}";
const USER_AVATAR = "{user_av_url_js}";
let history = [];
function addMessage(role, content){{
    const list = document.getElementById('messageList');
    const msg = document.createElement('div');
    msg.className = 'msg ' + role;
    const t = new Date().toLocaleTimeString('zh-CN',{{hour:'2-digit',minute:'2-digit'}});
    const d = document.createElement('div');
    d.textContent = content;
    const avStyle = role === 'bot'
        ? 'style="background-image:url(' + BOT_AVATAR + ');background-size:cover;background-position:center"'
        : 'style="background-image:url(' + USER_AVATAR + ');background-size:cover;background-position:center"';
    msg.innerHTML = '<div class="msg-avatar" ' + avStyle + '></div><div><div class="msg-bubble">' + d.innerHTML + '</div><div class="msg-time">' + t + '</div></div>';
    list.appendChild(msg);
    list.scrollTop = list.scrollHeight;
}}
function fillMsg(t){{document.getElementById('msgInput').value=t;document.getElementById('msgInput').focus()}}
async function sendMsg(){{
    const i = document.getElementById('msgInput');
    const m = i.value.trim();
    if(!m)return;
    i.value='';i.style.height='auto';
    addMessage('user',m);
    history.push({{role:'user',content:m}});

    // 创建 bot 消息容器（用变量引用，不用 id）
    const list = document.getElementById('messageList');
    const botMsg = document.createElement('div');
    botMsg.className = 'msg bot';
    const t = new Date().toLocaleTimeString('zh-CN',{{hour:'2-digit',minute:'2-digit'}});
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    const timeDiv = document.createElement('div');
    timeDiv.className = 'msg-time';
    timeDiv.textContent = t;
    const innerDiv = document.createElement('div');
    innerDiv.appendChild(bubble);
    innerDiv.appendChild(timeDiv);
    const av = document.createElement('div');
    av.className = 'msg-avatar';
    av.style.cssText = 'background-image:url(' + BOT_AVATAR + ');background-size:cover;background-position:center';
    botMsg.appendChild(av);
    botMsg.appendChild(innerDiv);
    list.appendChild(botMsg);
    list.scrollTop = list.scrollHeight;

    try{{
        const resp = await fetch('/api/chat/stream',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:m,history}})}});
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let full = '';
        while(true){{
            const {{done,value}} = await reader.read();
            if(done)break;
            const chunk = decoder.decode(value,{{stream:true}});
            const lines = chunk.split('\\n');
            for(const line of lines){{
                if(line.startsWith('data: ')){{
                    try{{
                        const d = JSON.parse(line.slice(6));
                        full = d.full;
                        bubble.textContent = full;
                        list.scrollTop = list.scrollHeight;
                    }}catch(e){{}}
                }}
            }}
        }}
        history.push({{role:'assistant',content:full}});
        updateStatus();
    }}catch(e){{addMessage('bot','连接断开，请检查服务是否在运行。')}}
}}
async function updateStatus(){{
    try{{
        const r = await fetch('/api/status');const d = await r.json();
        document.getElementById('statusText').textContent = d.status;
        document.getElementById('statusPanel').textContent = d.detail;
        document.getElementById('memoryPanel').textContent = d.memory;
    }}catch(e){{}}
}}
async function clearChat(){{
    history=[];document.getElementById('messageList').innerHTML='';
    addMessage('bot','对话已清空。有什么想聊的？');
    try{{const r = await fetch('/api/clear',{{method:'POST'}});const d = await r.json();document.getElementById('memoryPanel').textContent=d.memory;}}catch(e){{}}
}}
document.getElementById('msgInput').addEventListener('input',function(){{this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px'}});
updateStatus();
</script>
</body>
</html>"""

out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"index.html 已生成: {out_path}")
