"""Mark screenshots and compose a side-by-side comparison image.

Usage (in your own script):
    from compare_panels import panel, compose, RED, GRN, AMB
    web = panel("web.png", crop=(0, 500, 800, 1000), boxes=[(160, 830, 640, 885, GRN, "Continue")])
    an  = panel("and.png", crop=(0, 700, 1080, 1500), boxes=[(42, 1328, 1038, 1475, GRN, "Continue")])
    ios = panel("ios.png", crop=(0, 2000, 1206, 2622), boxes=[(485, 2140, 725, 2200, RED, "counter")])
    compose("out.png", "1. Text question, answer typed", [
        ("WEB", web, [(GRN, "matches the mock")]),
        ("ANDROID", an, [(GRN, "matches the mock")]),
        ("iOS", ios, [(RED, "counter shown (mock: none)")])])

Boxes are (x0, y0, x1, y1, colour, label) in the source image's pixels; an empty label draws the box only.
Colours: RED differs from the source of truth, GRN matches it, AMB a different pattern with no source.
Needs Pillow. Set FONT to a TTF/TTC path on your system.
"""
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Helvetica.ttc"  # macOS; change on Linux/Windows
RED, GRN, AMB = (235, 64, 52), (46, 170, 100), (240, 170, 30)


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def panel(path, crop, boxes, scale=1.0):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1, colour, label in boxes:
        x0, y0, x1, y1 = [v * scale for v in (x0, y0, x1, y1)]
        d.rectangle([x0, y0, x1, y1], outline=colour, width=max(4, im.width // 150))
        if not label:
            continue
        f = font(max(22, im.width // 28), True)
        tw, th = d.textlength(label, font=f), f.size + 8
        ty = y0 - th - 2 if y0 - th - 2 > crop[1] * scale else y1 + 2
        tx = min(max(x0, 4), im.width - tw - 12)
        d.rectangle([tx, ty, tx + tw + 10, ty + th], fill=colour)
        d.text((tx + 5, ty + 2), label, font=f, fill="white")
    return im.crop([int(v * scale) for v in crop])


def compose(out, title, columns, width=420, pad=16, head=46):
    """columns: [(name, panel_image, [(colour, caption), ...]), ...]"""
    cap, capb = font(17), font(17, True)
    panels = []
    for name, img, caps in columns:
        h = int(img.height * width / img.width)
        panels.append((name, img.resize((width, h), Image.LANCZOS), caps))
    maxh = max(p[1].height for p in panels)
    cap_h = max(len(c[2]) for c in panels) * 46 + 20
    total_w = len(panels) * width + (len(panels) + 1) * pad
    total_h = 14 + head + maxh + cap_h + pad
    canvas = Image.new("RGB", (total_w, total_h), (246, 247, 250))
    d = ImageDraw.Draw(canvas)
    for i, (name, img, caps) in enumerate(panels):
        x, y = pad + i * (width + pad), 14
        d.rectangle([x, y, x + width, y + head - 6], fill=(60, 64, 74))
        d.text((x + 12, y + 8), name, font=font(26, True), fill="white")
        canvas.paste(img, (x, y + head))
        cy = y + head + maxh + 10
        for colour, text in caps:
            d.ellipse([x, cy + 4, x + 16, cy + 20], fill=colour)
            line, ly = "", cy
            for w in text.split():
                if d.textlength(line + " " + w, font=cap) > width - 26:
                    d.text((x + 24, ly), line, font=cap, fill=(30, 34, 42)); ly += 22; line = w
                else:
                    line = (line + " " + w).strip()
            d.text((x + 24, ly), line, font=cap, fill=(30, 34, 42)); cy = ly + 30
    canvas.save(out, quality=88)
    return out
