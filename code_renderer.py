import tkinter as tk
import canvas_store

def update_code(code_area):
    code_area.delete("1.0", tk.END)

    def render(b, indent=0):
        pad = "    " * indent
        if b.data["nested"]:
            lines = []
            for line in b.data["template"].split('\n'):
                if "{child_code}" in line:
                    for c in b.child_blocks:
                        lines += render(c, indent + 1).split('\n')
                else:
                    lines.append(pad + line)
            return '\n'.join(lines)
        else:
            return pad + b.code

    tops = [b for b in canvas_store.code_blocks if not any(b in p.child_blocks for p in canvas_store.block_instances)]
    code_area.insert(tk.END, "\n\n".join(render(b) for b in tops))
