"""
桌面小宠：芙莉莲
动态状态：空闲、打字、睡眠
"""
import os
import sys
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import threading
import time
import webbrowser
import json
import urllib.request

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ASSETS_DIR

CHAT_URL = "http://127.0.0.1:7860"
PET_SIZE = 150


class DesktopPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("分身")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")
        self.root.configure(bg="#010101")
        self.root.geometry(f"{PET_SIZE+40}x{PET_SIZE+60}+200+200")

        self.state = "idle"  # idle, typing, sleep
        self.images = {}     # state -> PhotoImage

        # 状态到图片的映射
        self.state_images = {
            "idle":   "0bbf06fd868e34cb57ae8d0cf4674e212837cbd074815-GaeJot_fw658.webp",
            "typing": "bad5810bf7ca97fa71a0a8284b455fd3a3f6385f73e31-y6OEuO_fw658.webp",
            "sleep":  "0bbf06fd868e34cb57ae8d0cf4674e212837cbd074815-GaeJot_fw658.webp",
        }
        self.load_images()

        # 主画布
        self.canvas = tk.Canvas(
            self.root, width=PET_SIZE+40, height=PET_SIZE+60,
            bg="#010101", highlightthickness=0,
        )
        self.canvas.pack()

        # 角色图像
        self.img_display = None

        # 状态标签（小宠上方）
        self.state_label = self.canvas.create_text(
            (PET_SIZE+40)//2, 8, text="",
            fill="#b088c8", font=("Microsoft YaHei", 9, "bold"),
            anchor="n",
        )

        # 绿色状态点
        self.status_dot = self.canvas.create_oval(
            PET_SIZE+20, 5, PET_SIZE+32, 17,
            fill="#4ade80", outline="",
        )

        # 交互
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<Double-Button-1>", self.open_chat)
        self.canvas.bind("<Button-3>", self.show_menu)

        # 右键菜单
        self.menu = tk.Menu(self.root, tearoff=0, bg="#2a1a3a", fg="white", font=("Microsoft YaHei", 9))
        self.menu.add_command(label="打开聊天", command=self.open_chat)
        self.menu.add_command(label="检查状态", command=self.check_status)
        self.menu.add_separator()
        self.menu.add_command(label="退出", command=self.root.quit)

        # 提示气泡
        self.tooltip = None

        # 初始显示
        self.set_state("idle")

        # 后台线程
        self.running = True
        self.check_server_status()
        self.state_loop()

    def load_images(self):
        for state, filename in self.state_images.items():
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                w, h = img.size
                ratio = PET_SIZE / max(w, h)
                new_w, new_h = int(w * ratio), int(h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)

                # 睡眠状态：变暗 + 模糊
                if state == "sleep":
                    img = img.filter(ImageFilter.GaussianBlur(radius=3))
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(0.5)

                self.images[state] = ImageTk.PhotoImage(img)
                print(f"[小宠] 加载 {state}: {filename}")

    def set_state(self, state):
        if state in self.images:
            self.state = state
            if self.img_display:
                self.canvas.delete(self.img_display)
            cx = (PET_SIZE+40) // 2
            cy = (PET_SIZE+60) // 2
            self.img_display = self.canvas.create_image(cx, cy, image=self.images[state], anchor="center")

            # 更新标签
            labels = {"idle": "✦ 空闲中", "typing": "✎ 思考中...", "sleep": "💤 睡眠中"}
            self.canvas.itemconfig(self.state_label, text=labels.get(state, ""))
            self.root.update()

    def on_mouse_enter(self, event):
        pass

    def on_mouse_leave(self, event):
        pass

    def state_loop(self):
        """状态循环：通过 API 查询聊天状态"""
        def check():
            while self.running:
                try:
                    resp = urllib.request.urlopen(f"{CHAT_URL}/api/activity", timeout=2)
                    data = json.loads(resp.read())
                    s = data.get("status", "idle")
                    new_state = {"chatting": "typing", "idle": "idle", "sleep": "sleep"}.get(s, "idle")
                    if new_state != self.state:
                        self.root.after(0, lambda ns=new_state: self.set_state(ns))
                except:
                    # 服务器未运行
                    pass
                time.sleep(3)
        threading.Thread(target=check, daemon=True).start()
        # 清理旧的 last_activity 相关逻辑

    def start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")
        if self.state == "sleep":
            self.root.after(0, lambda: self.set_state("idle"))

    def open_chat(self, event=None):
        webbrowser.open(CHAT_URL)

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def check_server_status(self):
        def check():
            while self.running:
                try:
                    urllib.request.urlopen(f"{CHAT_URL}/api/status", timeout=2)
                    self.root.after(0, lambda: self.canvas.itemconfig(self.status_dot, fill="#4ade80"))
                except:
                    self.root.after(0, lambda: self.canvas.itemconfig(self.status_dot, fill="#ef4444"))
                time.sleep(10)
        threading.Thread(target=check, daemon=True).start()

    def check_status(self):
        try:
            resp = urllib.request.urlopen(f"{CHAT_URL}/api/status", timeout=3)
            data = json.loads(resp.read())
            status = data.get("detail", "运行中")
        except:
            status = "服务器未运行"
        popup = tk.Toplevel(self.root)
        popup.title("状态")
        popup.geometry(f"+{self.root.winfo_x()+30}+{self.root.winfo_y()+30}")
        popup.attributes("-topmost", True)
        tk.Label(popup, text=status, padx=12, pady=8, font=("Microsoft YaHei", 9)).pack()
        tk.Button(popup, text="确定", command=popup.destroy).pack(pady=5)

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.running = False


if __name__ == "__main__":
    pet = DesktopPet()
    pet.run()
