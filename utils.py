import canvas_store

def draw_connections(canvas):
    canvas.delete("line")
    for b in canvas_store.block_instances:
        if b.data["nested"]:
            for c in b.child_blocks:
                bx, by = b.x + 200, b.y + 30
                cx, cy = c.x, c.y + 30
                canvas.create_line(
                    bx, by, (bx + cx) // 2, by, (bx + cx) // 2, cy, cx, cy,
                    fill="#999", width=2, smooth=True, tags="line"
                )

def auto_align(parent, canvas):
    y0 = parent.y + 70
    height = 60 + len(parent.child_blocks) * 70
    canvas.coords(parent.rect, parent.x, parent.y, parent.x + 220, parent.y + height)
    canvas.coords(parent.text, parent.x + 110, parent.y + 30)

    for ch in parent.child_blocks:
        canvas.coords(ch.rect, parent.x + 20, y0, parent.x + 200, y0 + 60)
        canvas.coords(ch.text, parent.x + 110, y0 + 30)
        ch.x, ch.y = parent.x + 20, y0
        y0 += 70

tooltip_id = None

def show_tooltip(event, block):
    global tooltip_id
    tooltip_id = block.canvas.create_text(
        block.x + 100, block.y - 10,
        text=block.code or "코드 없음",
        font=("Courier", 9), fill="gray", tags="tooltip"
    )

def hide_tooltip(event):
    global tooltip_id
    if tooltip_id:
        event.widget.delete(tooltip_id)
        tooltip_id = None

def copy_block():
    b = canvas_store.drag_data["item"]
    if b:
        canvas_store.clipboard = {
            "label": b.label,
            "data": b.data,
            "code": b.code
        }

def paste_block(canvas, code_area):
    if canvas_store.clipboard:
        from blocks import Block
        b = Block(canvas_store.clipboard["label"], canvas_store.clipboard["data"],
                  20, 20 + len(canvas_store.block_instances) * 70,
                  canvas, code_area)
        b.code = canvas_store.clipboard["code"]
        canvas_store.code_blocks.append(b)
        from code_renderer import update_code
        update_code(code_area)

def delete_block(canvas, code_area):
    b = canvas_store.drag_data["item"]
    if b:
        canvas.delete(b.rect)
        canvas.delete(b.text)
        if b in canvas_store.block_instances:
            canvas_store.block_instances.remove(b)
        if b in canvas_store.code_blocks:
            canvas_store.code_blocks.remove(b)
        for p in canvas_store.block_instances:
            if b in p.child_blocks:
                p.child_blocks.remove(b)
        from code_renderer import update_code
        update_code(code_area)
