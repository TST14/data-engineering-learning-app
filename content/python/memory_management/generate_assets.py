"""Generate lightweight educational animated GIFs for this topic.

Run from anywhere in the repo:
    python content/python/memory_management/generate_assets.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Assets folder is always next to this script — no fragile relative paths.
ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

W, H = 680, 300
BG = (248, 250, 255)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _font(size, bold=False):
    """Return a font, falling back to Pillow's bundled font."""
    candidates = [
        f"C:/Windows/Fonts/{'arialbd' if bold else 'arial'}.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-{}.ttf".format(
            "Bold" if bold else "Regular"
        ),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf".format(
            "-Bold" if bold else ""
        ),
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def _canvas(w=W, h=H):
    img = Image.new("RGB", (w, h), BG)
    return img, ImageDraw.Draw(img)


def _caption_bar(d, w, h, text):
    d.rectangle([(0, h - 42), (w, h)], fill=(220, 220, 228))
    d.text((16, h - 30), text, fill=(50, 50, 60), font=_font(13))


def _save(frames, name, duration=1000):
    path = ASSETS_DIR / name
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        loop=0,
        duration=duration,
    )
    kb = path.stat().st_size // 1024
    print(f"  ✓  {name}  ({kb} KB, {len(frames)} frames)")


# ── GIF 1: Reference Counting ─────────────────────────────────────────────────

def make_ref_counting():
    # steps: (code_caption, active_vars: list[str], refcount, freed)
    steps = [
        ("# Before any assignment",          [],              0, False),
        ('a = "hello"',                       ["a"],           1, False),
        ("b = a",                             ["a", "b"],      2, False),
        ("c = a",                             ["a", "b", "c"], 3, False),
        ("del b",                             ["a", "c"],      2, False),
        ('c = "world"  # c points elsewhere', ["a"],           1, False),
        ("del a   →   refcount = 0 → FREED ♻️", [],            0, True),
    ]

    OBJ_X, OBJ_Y, OBJ_W, OBJ_H = 420, 80, 210, 115
    ALL_VARS = ["a", "b", "c"]

    frames = []
    for code, active, rc, freed in steps:
        img, d = _canvas()

        # Title
        d.text((16, 12), "Reference Counting", fill=(20, 60, 130), font=_font(17, bold=True))
        d.text((16, 36), "Every object carries a counter. When it hits 0, memory is freed immediately.", fill=(80, 80, 90), font=_font(11))

        # Stack panel
        d.rectangle([(16, 62), (360, 235)], fill=(240, 248, 240), outline=(100, 160, 100), width=2)
        d.text((24, 68), "STACK  — variable names", fill=(30, 110, 30), font=_font(12, bold=True))

        for i, var in enumerate(ALL_VARS):
            vy = 96 + i * 44
            is_active = var in active
            box_fill   = (185, 235, 185) if is_active else (218, 218, 218)
            text_color = (20, 80, 20)    if is_active else (155, 155, 155)
            d.rectangle([(28, vy), (220, vy + 30)], fill=box_fill, outline=(120, 120, 120), width=1)
            label = f'  {var}  →  "hello"' if is_active else f'  {var}  (not active)'
            d.text((32, vy + 7), label, fill=text_color, font=_font(12))

            # Arrow toward heap object
            if is_active:
                ax1, ay1 = 222, vy + 15
                ax2, ay2 = OBJ_X - 2, OBJ_Y + OBJ_H // 2
                d.line([(ax1, ay1), (ax2, ay2)], fill=(70, 110, 200), width=2)
                # arrowhead
                d.polygon(
                    [(ax2, ay2), (ax2 - 10, ay2 - 5), (ax2 - 10, ay2 + 5)],
                    fill=(70, 110, 200),
                )

        # Heap object box
        obj_fill   = (255, 195, 195) if freed else (200, 222, 255)
        obj_border = (200, 50, 50)   if freed else (80, 130, 210)
        d.rectangle(
            [(OBJ_X, OBJ_Y), (OBJ_X + OBJ_W, OBJ_Y + OBJ_H)],
            fill=obj_fill, outline=obj_border, width=2,
        )
        d.text((OBJ_X + 10, OBJ_Y + 6),  "HEAP — object",      fill=(50, 50, 130), font=_font(12, bold=True))
        d.text((OBJ_X + 10, OBJ_Y + 28), 'type : str',          fill=(70, 70, 80),  font=_font(12))
        d.text((OBJ_X + 10, OBJ_Y + 46), 'value: "hello"',      fill=(70, 70, 80),  font=_font(12))
        rc_col = (200, 0, 0) if freed else (0, 140, 0)
        d.text((OBJ_X + 10, OBJ_Y + 68), f"refcount: {rc}",     fill=rc_col,        font=_font(14, bold=True))

        if freed:
            d.text((OBJ_X + 20, OBJ_Y - 26), "FREED — memory returned ♻️", fill=(200, 0, 0), font=_font(13, bold=True))

        _caption_bar(d, W, H, f">>> {code}")
        frames.append(img)

    frames += [frames[-1]] * 3
    _save(frames, "01_reference_counting.gif", duration=1100)


# ── GIF 2: Stack Frames ───────────────────────────────────────────────────────

def make_stack_frames():
    W2, H2 = 560, 380
    STACK_LEFT = 140
    FRAME_W, FRAME_H = 280, 54
    STACK_BOTTOM = 320

    PALETTE = [
        ((200, 225, 255), (80, 130, 200)),   # global  — blue
        ((195, 255, 210), (60, 170, 80)),    # calculate — green
        ((255, 230, 175), (200, 145, 40)),   # multiply  — orange
    ]

    steps = [
        ([], "Program starts — empty call stack"),
        (["Global Frame  (final = ?)"], "Global frame on stack"),
        (["Global Frame  (final = ?)", "calculate()  x, y, answer"], "calculate() called — frame pushed ↑"),
        (["Global Frame  (final = ?)", "calculate()  x, y, answer", "multiply()  a, b, result"], "multiply() called — frame pushed ↑"),
        (["Global Frame  (final = ?)", "calculate()  x, y, answer"], "multiply() returns — frame POPPED ✓"),
        (["Global Frame  (final = ?)"], "calculate() returns — frame POPPED ✓"),
        (["Global Frame  (final = 50)"], "Result stored in Global frame  🎉"),
    ]

    frames = []
    for stack, caption in steps:
        img, d = _canvas(W2, H2)

        d.text((16, 14), "Stack Frames (LIFO)", fill=(20, 60, 130), font=_font(17, bold=True))
        d.text((16, 40), "Each function call pushes a frame; return pops it.", fill=(80, 80, 90), font=_font(11))

        # Stack border
        d.rectangle(
            [(STACK_LEFT - 12, 62), (STACK_LEFT + FRAME_W + 12, STACK_BOTTOM + 12)],
            fill=(244, 244, 248), outline=(160, 160, 170), width=1,
        )
        d.text((STACK_LEFT + 80, 68), "STACK", fill=(100, 100, 170), font=_font(11, bold=True))

        for i, name in enumerate(stack):
            fy = STACK_BOTTOM - (i + 1) * (FRAME_H + 5)
            fill, border = PALETTE[min(i, 2)]
            d.rectangle(
                [(STACK_LEFT, fy), (STACK_LEFT + FRAME_W, fy + FRAME_H)],
                fill=fill, outline=border, width=2,
            )
            d.text((STACK_LEFT + 10, fy + 8), name, fill=(30, 30, 80), font=_font(12))

            # TOP pointer for topmost frame
            if i == len(stack) - 1:
                mid_y = fy + FRAME_H // 2
                d.text((STACK_LEFT - 72, mid_y - 8), "TOP →", fill=(180, 50, 50), font=_font(12, bold=True))

        # Bottom label
        d.rectangle([(0, H2 - 46), (W2, H2)], fill=(220, 220, 228))
        d.text((16, H2 - 34), caption, fill=(50, 50, 60), font=_font(13))

        frames.append(img)

    frames += [frames[-1]] * 3
    _save(frames, "02_stack_frames.gif", duration=1150)


# ── GIF 3: GC Generations ─────────────────────────────────────────────────────

def make_gc_generations():
    W3, H3 = 680, 320
    GEN_ROWS = [
        (78,  "Gen 0  — young objects, checked MOST often", (190, 220, 255), (70, 120, 200)),
        (168, "Gen 1  — survived at least one GC sweep",    (190, 255, 205), (60, 175, 80)),
        (258, "Gen 2  — long-lived objects, collected RARELY", (255, 225, 150), (200, 155, 40)),
    ]
    R = 18  # circle radius

    def row_positions(count, cy):
        if count == 0:
            return []
        margin = 120
        gap = max(38, (W3 - 2 * margin) // max(count, 1))
        return [(margin + i * gap + R, cy) for i in range(count)]

    def draw_gen_frame(label, alive0, dying0, alive1, dying1, alive2):
        img, d = _canvas(W3, H3)
        d.text((16, 10), "GC Generations — How Objects Age", fill=(20, 60, 130), font=_font(17, bold=True))
        d.text((16, 34), "New objects start in Gen 0. Survivors are promoted. Short-lived ones are swept.", fill=(80, 80, 90), font=_font(11))

        for (gy, glabel, gcol, gborder), alive, dying in zip(
            GEN_ROWS,
            [alive0, alive1, alive2],
            [dying0, dying1, 0],
        ):
            # Lane
            d.rectangle([(16, gy - R - 12), (W3 - 16, gy + R + 12)],
                        fill=tuple(min(c + 40, 255) for c in gcol),
                        outline=gborder, width=1)
            d.text((22, gy - R - 10), glabel, fill=(40, 40, 40), font=_font(11, bold=True))

            total = alive + dying
            positions = row_positions(total, gy)

            for j, (cx, cy) in enumerate(positions):
                if j < dying:
                    # dying — red with X
                    d.ellipse([(cx - R, cy - R), (cx + R, cy + R)],
                              fill=(255, 195, 195), outline=(200, 50, 50), width=2)
                    d.text((cx - 6, cy - 8), "✕", fill=(200, 0, 0), font=_font(14, bold=True))
                else:
                    # alive — generation color
                    d.ellipse([(cx - R, cy - R), (cx + R, cy + R)],
                              fill=gcol, outline=gborder, width=2)
                    d.text((cx - 4, cy - 7), "●", fill=(40, 40, 90), font=_font(12))

        _caption_bar(d, W3, H3, label)
        return img

    steps = [
        # (label, alive0, dying0, alive1, dying1, alive2)
        ("8 new objects created — all land in Generation 0",                  8, 0, 0, 0, 0),
        ("GC sweeps Gen 0 — 4 short-lived objects collected 🗑️",             4, 4, 0, 0, 0),
        ("4 survivors promoted to Generation 1",                              0, 0, 4, 0, 0),
        ("Gen 1 sweep — 2 objects collected; 2 survive",                      0, 0, 2, 2, 0),
        ("2 long-lived objects promoted to Generation 2 (rarely collected)",  0, 0, 0, 0, 2),
        ("Summary: most objects die young; long-lived ones age into Gen 2",   0, 0, 0, 0, 2),
    ]

    frames = []
    for args in steps:
        frames.append(draw_gen_frame(*args))

    frames += [frames[-1]] * 3
    _save(frames, "03_gc_generations.gif", duration=1300)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Generating GIFs → {ASSETS_DIR}\n")
    make_ref_counting()
    make_stack_frames()
    make_gc_generations()
    print("\nDone!")
