# blocks.py

import tkinter as tk
from tkinter import simpledialog
import canvas_store
from utils import draw_connections, auto_align, show_tooltip, hide_tooltip
from code_renderer import update_code

class Block:
    def __init__(self, label, data, x, y, canvas, code_area):
        self.label = label
        self.data = data
        self.x, self.y = x, y
        self.code = ""
        self.child_blocks = []
        self.canvas = canvas
        self.code_area = code_area
        self.clicked = False

        self.rect = canvas.create_rectangle(
            x, y, x + 200, y + 60,
            fill=data["color"], outline="#888", width=2, tags="block"
        )
        self.text = canvas.create_text(
            x + 100, y + 30, text=label,
            font=("Comic Sans MS", 12, "bold"), tags="block"
        )

        canvas_store.block_instances.append(self)

        for tag in (self.rect, self.text):
            canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
            canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_drop)
            canvas.tag_bind(tag, "<Enter>", lambda e: show_tooltip(e, self))
            canvas.tag_bind(tag, "<Leave>", hide_tooltip)

    def on_press(self, e):
        canvas_store.drag_data["item"] = self
        canvas_store.drag_data["x"] = e.x
        canvas_store.drag_data["y"] = e.y

    def on_drag(self, e):
        dx = e.x - canvas_store.drag_data["x"]
        dy = e.y - canvas_store.drag_data["y"]
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        self.x += dx
        self.y += dy
        canvas_store.drag_data["x"] = e.x
        canvas_store.drag_data["y"] = e.y
        draw_connections(self.canvas)

    def on_drop(self, e):
        if self.clicked:
            return
        self.clicked = True

        # ✨ 드롭 시 반짝 효과
        original = self.data["color"]
        self.canvas.itemconfig(self.rect, fill="#fffacd")
        self.canvas.after(150, lambda: self.canvas.itemconfig(self.rect, fill=original))

        # 📜 템플릿 기반 코드 채우기
        tpl = self.data["template"]
        code = tpl

        if "{name}" in tpl:
            name = simpledialog.askstring("변수 이름", "변수 이름을 입력하세요:")
            if not name:
                return
            code = code.replace("{name}", name)

        if "{value}" in tpl:
            val = simpledialog.askstring("값 입력", "값을 입력하세요:")
            if val is None:
                return
            code = code.replace("{value}", val.strip('\'"'))

        self.code = code

        # 🧲 부모 블록에 붙이기
        if not self.data["nested"]:
            for p in canvas_store.block_instances:
                if p is not self and p.data.get("nested"):
                    x1, y1, x2, y2 = self.canvas.coords(p.rect)
                    pad = 10
                    if x1 - pad < self.x < x2 + pad and y1 - pad < self.y < y2 + pad:
                        self.x = p.x + 20
                        self.y = p.y + 70 + len(p.child_blocks) * 70
                        self.canvas.coords(self.rect, self.x, self.y, self.x + 180, self.y + 60)
                        self.canvas.coords(self.text, self.x + 90, self.y + 30)

                        # ✨ 부모 반짝 효과
                        self.canvas.itemconfig(p.rect, outline="gold", width=3)
                        self.canvas.after(150, lambda: self.canvas.itemconfig(p.rect, outline="#888", width=2))

                        p.child_blocks.append(self)
                        auto_align(p, self.canvas)
                        draw_connections(self.canvas)
                        update_code(self.code_area)
                        return

        # 🧠 코드 블록 목록 등록
        if self not in canvas_store.code_blocks:
            canvas_store.code_blocks.append(self)

        update_code(self.code_area)
        draw_connections(self.canvas)
