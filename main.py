import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, filedialog
from config import BLOCKS, THEMES
from blocks import Block
import canvas_store
from code_renderer import update_code
from logic import run_code, save_to_file, run_file
from utils import copy_block, paste_block, delete_block
from sb3_parser import parse_sb3, opcode_to_pyblock

spawn_counter = 0
current_py_path = None
current_theme = "기본"

root = tk.Tk()
root.title("PyBlock")
root.geometry("1000x850")
root.configure(bg=THEMES["기본"])

# ────────── 테마 전환 ──────────
def switch_theme():
    global current_theme
    new = "민트" if current_theme == "기본" else "기본"
    current_theme = new
    bg = THEMES[new]
    root.configure(bg=bg)
    palette_frame.configure(bg=bg)
    canvas.configure(bg=bg)
    center_frame.configure(bg=bg)
    left_frame.configure(bg=bg)
    right_frame.configure(bg=bg)
    btn_frame.configure(bg=bg)

# ────────── 팔레트 ──────────
palette_frame = tk.Frame(root, bg=THEMES["기본"])
palette_frame.pack(fill=tk.X, pady=5)

def add_palette_button(label):
    btn = tk.Button(palette_frame, text=label,
                    bg=BLOCKS[label]["color"],
                    font=("Comic Sans MS", 10),
                    command=lambda l=label: spawn_block(l))
    btn.pack(side=tk.LEFT, padx=4, pady=4)

for lbl in BLOCKS:
    add_palette_button(lbl)

def create_custom_block():
    name = simpledialog.askstring("블록 이름", "새 블록 이름:")
    if not name: return
    tpl = simpledialog.askstring("템플릿", "파이썬 템플릿 입력:")
    if tpl is None: return
    nested = messagebox.askyesno("중첩 여부", "자식 블록 허용?")
    BLOCKS[name] = {"template": tpl, "color": "#DAF7A6", "nested": nested}
    add_palette_button(name)

tk.Button(palette_frame, text="➕ 사용자 정의 블록",
          command=create_custom_block, bg="#a2d5ab",
          font=("Comic Sans MS", 10)).pack(side=tk.RIGHT, padx=4)

tk.Button(palette_frame, text="🎨 테마 바꾸기",
          command=switch_theme, bg="#fce4ec",
          font=("Comic Sans MS", 10)).pack(side=tk.RIGHT, padx=4)

def load_sb3():
    path = filedialog.askopenfilename(filetypes=[("Scratch 파일", "*.sb3")])
    if not path: return
    try:
        sb3_blocks = parse_sb3(path)
        y = 20
        for blk in sb3_blocks:
            converted = opcode_to_pyblock(blk["opcode"], blk["fields"])
            if converted:
                label, data = converted
                Block(label, data, 20, y, canvas, code_area)
                y += 80
    except Exception as e:
        messagebox.showerror("불러오기 실패", str(e))

tk.Button(palette_frame, text="📁 .sb3 불러오기",
          command=load_sb3, bg="#ffe0b3",
          font=("Comic Sans MS", 10)).pack(side=tk.RIGHT, padx=4)

# ────────── 캔버스 ──────────
canvas = tk.Canvas(root, bg=THEMES["기본"], height=360)
canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

def spawn_block(label):
    global spawn_counter
    data = BLOCKS[label]
    Block(label, data, 20, 20 + spawn_counter * 70, canvas, code_area)
    spawn_counter += 1

# ────────── 코드 & 출력 좌우 배치 ──────────
center_frame = tk.Frame(root, bg=THEMES["기본"])
center_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

left_frame = tk.Frame(center_frame, bg=THEMES["기본"])
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(left_frame, text="🔎 생성된 파이썬 코드",
         bg=THEMES["기본"], font=("Comic Sans MS", 12, "bold")).pack(anchor="w")

code_area = scrolledtext.ScrolledText(left_frame, height=15,
    font=("Courier", 11))
code_area.pack(fill=tk.BOTH, expand=True)

btn_frame = tk.Frame(left_frame, bg=THEMES["기본"])
btn_frame.pack(fill=tk.X, pady=5)

def run_code_from_area():
    src = code_area.get("1.0", tk.END)
    run_code(src, output_area)

def save_code_to_file():
    global current_py_path
    src = code_area.get("1.0", tk.END)
    path = save_to_file(src)
    if path:
        current_py_path = path

def run_saved_file():
    run_file(current_py_path, output_area)

tk.Button(btn_frame, text="▶ 실행", command=run_code_from_area,
          bg="#4CAF50", fg="white",
          font=("Comic Sans MS", 10)).pack(side=tk.LEFT)

tk.Button(btn_frame, text="💾 저장", command=save_code_to_file,
          bg="#2196F3", fg="white",
          font=("Comic Sans MS", 10)).pack(side=tk.LEFT, padx=5)

tk.Button(btn_frame, text="▶ 파일 실행", command=run_saved_file,
          bg="#FF5722", fg="white",
          font=("Comic Sans MS", 10)).pack(side=tk.LEFT)

right_frame = tk.Frame(center_frame, bg=THEMES["기본"])
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

tk.Label(right_frame, text="🧾 실행 결과",
         bg=THEMES["기본"], font=("Comic Sans MS", 12, "bold")).pack(anchor="w")

output_area = scrolledtext.ScrolledText(right_frame, height=15,
    font=("Courier", 11), bg="#f9f9f9")
output_area.pack(fill=tk.BOTH, expand=True)

# ────────── 단축키 ──────────
# ────────── 단축키 ──────────
root.bind("<Control-c>", lambda e: copy_block())
root.bind("<Control-v>", lambda e: paste_block(canvas, code_area))
root.bind("<Delete>", lambda e: delete_block(canvas, code_area))

# ────────── 앱 실행 ──────────
root.mainloop()
