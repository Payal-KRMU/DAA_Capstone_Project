"""render_trace.py - turns a text output trace into a terminal-style PNG screenshot."""
import sys
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def render(lines, out, title="Terminal - python main.py"):
    font = ImageFont.truetype(FONT, 15)
    lh = 20
    width = max(900, max(int(font.getlength(l)) for l in lines) + 40)
    img = Image.new("RGB", (width, len(lines) * lh + 60), (30, 30, 36))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, width, 30], fill=(52, 52, 60))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([12 + i * 22, 9, 24 + i * 22, 21], fill=c)
    d.text((90, 7), title, font=font, fill=(200, 200, 200))
    for i, l in enumerate(lines):
        color = (230, 230, 230)
        if l.startswith("$"): color = (120, 220, 120)
        elif l.startswith("[PHASE") or l.startswith("==="): color = (110, 180, 255)
        elif "LATE" in l: color = (255, 120, 120)
        elif "ON TIME" in l or l.startswith("OK"): color = (140, 230, 140)
        d.text((20, 40 + i * lh), l, font=font, fill=color)
    img.save(out)


if __name__ == "__main__":
    src, out, start, end = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    cmd = sys.argv[5] if len(sys.argv) > 5 else None
    lines = open(src).read().splitlines()[start:end]
    render(([f"$ {cmd}"] if cmd else []) + lines, out, title=f"Terminal - {cmd or 'output'}")
