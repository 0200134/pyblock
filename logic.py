import sys, io, subprocess, os
import tkinter as tk
from tkinter import filedialog, messagebox
import importlib, ast

def extract_modules(src):
    tree = ast.parse(src)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.add(node.module.split('.')[0])
    return mods

def ensure_modules(mods):
    for mod in mods:
        try:
            importlib.import_module(mod)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", mod])

def run_code(src, output_area):
    buf = io.StringIO()
    sys.stdout = buf
    try:
        mods = extract_modules(src)
        ensure_modules(mods)
        exec(src, {})
    except Exception as e:
        buf.write(f"오류: {e}")
    finally:
        sys.stdout = sys.__stdout__
    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, buf.getvalue())

def save_to_file(src):
    path = filedialog.asksaveasfilename(defaultextension=".py",
        filetypes=[("Python 파일", "*.py")])
    if not path: return None
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)
    messagebox.showinfo("저장 완료", f"{os.path.basename(path)}에 저장되었습니다.")
    return path

def run_file(path, output_area):
    if not path:
        messagebox.showwarning("실행 불가", "먼저 저장해주세요.")
        return
    proc = subprocess.run([sys.executable, path], capture_output=True, text=True)
    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, proc.stdout + proc.stderr)
