import os
import tkinter as tk
import threading

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

SEARCH_ROOT = os.path.expanduser("~")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
MAX_RESULTS = 7

KEY = "#010101"
GLASS = "#20202c"
GLASS_EDGE = "#4a4a60"
HIGHLIGHT = "#6f6f88"
PANEL = "#1a1a24"
FG = "#f2f2f7"
ACCENT = "#8ab4ff"

W = 460
PILL_H = 58
GAP = 8
HANDLE_H = 7
HANDLE_W = 90
ROW_H = 24
PAD = 8
TARGET_ALPHA = 0.92

file_index = []
current_results = []
panel_h = 0.0
target_panel_h = 0.0
anim_id = None
drag = {"active": False, "x": 0, "y": 0}
anchor = {"x": 0, "y": 0}


def build_index():
    for dirpath, dirnames, filenames in os.walk(SEARCH_ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames + dirnames:
            file_index.append((name.lower(), os.path.join(dirpath, name)))


def search(query):
    q = query.lower().strip()
    if not q:
        return []
    return [p for (n, p) in file_index if q in n][:MAX_RESULTS]


def round_rect(x1, y1, x2, y2, r, **kw):
    pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
           x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


def win_height():
    h = PAD + PILL_H
    if panel_h > 1:
        h += GAP + int(panel_h)
    return h + GAP + HANDLE_H + PAD


def place_window():
    h = win_height()
    root.geometry(f"{W}x{h}+{int(anchor['x']-W)}+{int(anchor['y']-h)}")


def redraw():
    place_window()
    canvas.delete("shape")
    h = win_height()
    canvas.configure(width=W, height=h)

    pill_top, pill_bot = PAD, PAD + PILL_H
    round_rect(6, pill_top, W-6, pill_bot, PILL_H//2,
               fill=GLASS, outline=GLASS_EDGE, width=1, tags="shape")
    canvas.create_line(28, pill_top+5, W-28, pill_top+5,
                       fill=HIGHLIGHT, width=1, tags="shape")
    canvas.coords(entry_item, W//2, (pill_top+pill_bot)//2)
    canvas.itemconfigure(entry_item, width=W-56)

    if panel_h > 1:
        p_top = pill_bot + GAP
        p_bot = p_top + int(panel_h)
        round_rect(6, p_top, W-6, p_bot, 22,
                   fill=PANEL, outline=GLASS_EDGE, width=1, tags="shape")
        canvas.coords(bottom_item, W//2, (p_top+p_bot)//2)
        canvas.itemconfigure(bottom_item, state="normal", width=W-28)
    else:
        canvas.itemconfigure(bottom_item, state="hidden")

    hy = h - PAD - HANDLE_H
    round_rect(W//2-HANDLE_W//2, hy, W//2+HANDLE_W//2, hy+HANDLE_H,
               HANDLE_H//2, fill="#ffffff", outline="", tags=("shape", "drag"))


def animate():
    global panel_h, anim_id
    diff = target_panel_h - panel_h
    if abs(diff) < 1:
        panel_h = target_panel_h
        redraw()
        anim_id = None
        return
    panel_h += diff * 0.35
    redraw()
    anim_id = root.after(16, animate)


def start_anim():
    global anim_id
    if anim_id is None:
        anim_id = root.after(0, animate)


def show_preview(path):
    if path.lower().endswith(IMAGE_EXTS):
        try:
            if HAS_PIL:
                img = Image.open(path)
                img.thumbnail((40, 40))
                photo = ImageTk.PhotoImage(img)
            else:
                photo = tk.PhotoImage(file=path)
                photo = photo.subsample(max(1, photo.width() // 40))
            preview.configure(image=photo)
            preview.image = photo
            return
        except Exception:
            pass
    preview.configure(image="")
    preview.image = None


def update_results(*args):
    global target_panel_h
    current_results.clear()
    current_results.extend(search(entry_var.get()))
    listbox.delete(0, tk.END)
    for p in current_results:
        tag = "[folder]  " if os.path.isdir(p) else ""
        listbox.insert(tk.END, tag + os.path.basename(p))
    if current_results:
        listbox.configure(height=len(current_results))
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(0)
        show_preview(current_results[0])
        target_panel_h = len(current_results) * ROW_H + 2 * PAD
    else:
        target_panel_h = 0
    start_anim()


def autofill(event):
    if current_results:
        entry_var.set(os.path.basename(current_results[0]))
        entry.icursor(tk.END)
    return "break"


def move(delta):
    if not current_results:
        return
    sel = listbox.curselection()
    idx = max(0, min(len(current_results)-1, (sel[0] if sel else 0) + delta))
    listbox.selection_clear(0, tk.END)
    listbox.selection_set(idx)
    show_preview(current_results[idx])


def open_selected(event=None):
    sel = listbox.curselection()
    idx = sel[0] if sel else 0
    if current_results and idx < len(current_results):
        os.startfile(current_results[idx])


def drag_start(event):
    drag["active"] = True
    drag["x"], drag["y"] = event.x_root, event.y_root


def drag_move(event):
    if drag["active"]:
        anchor["x"] += event.x_root - drag["x"]
        anchor["y"] += event.y_root - drag["y"]
        drag["x"], drag["y"] = event.x_root, event.y_root
        place_window()


root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.0)
try:
    root.attributes("-transparentcolor", KEY)
except tk.TclError:
    pass
root.configure(bg=KEY)

canvas = tk.Canvas(root, bg=KEY, highlightthickness=0, bd=0)
canvas.pack(fill="both", expand=True)

entry_var = tk.StringVar()
entry_var.trace_add("write", update_results)
entry = tk.Entry(canvas, textvariable=entry_var, font=("Segoe UI", 16),
                 bg=GLASS, fg=FG, insertbackground=ACCENT,
                 relief="flat", highlightthickness=0, bd=0)
entry_item = canvas.create_window(0, 0, window=entry, width=W-56, height=30)

bottom = tk.Frame(canvas, bg=PANEL)
listbox = tk.Listbox(bottom, font=("Segoe UI", 11), bg=PANEL, fg=FG,
                     selectbackground=ACCENT, selectforeground="#10101a",
                     relief="flat", highlightthickness=0, bd=0, activestyle="none")
listbox.pack(side="left", fill="both", expand=True, padx=(4, 0))
preview = tk.Label(bottom, bg=PANEL)
preview.pack(side="right", padx=8)
bottom_item = canvas.create_window(0, 0, window=bottom, width=W-28, state="hidden")

entry.bind("<Tab>", autofill)
entry.bind("<Return>", open_selected)
entry.bind("<Down>", lambda e: move(1))
entry.bind("<Up>", lambda e: move(-1))
root.bind("<Escape>", lambda e: root.destroy())
listbox.bind("<Double-Button-1>", open_selected)
canvas.tag_bind("drag", "<Button-1>", drag_start)
canvas.tag_bind("drag", "<B1-Motion>", drag_move)

root.update_idletasks()
anchor["x"] = root.winfo_screenwidth() - 30
anchor["y"] = root.winfo_screenheight() - 70
redraw()
entry.focus_force()


def fade_in(a=0.0):
    a = min(TARGET_ALPHA, a + 0.12)
    root.attributes("-alpha", a)
    if a < TARGET_ALPHA:
        root.after(16, lambda: fade_in(a))


root.after(60, fade_in)
threading.Thread(target=build_index, daemon=True).start()
root.mainloop()