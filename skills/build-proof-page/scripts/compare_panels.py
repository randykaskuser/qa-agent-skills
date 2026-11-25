"""Mark screenshots and compose a side-by-side comparison image.

Usage (in your own script):
    from compare_panels import panel, compose, RED, GRN, AMB
    web = panel("web.png", crop=(0, 500, 800, 1000), boxes=[(160, 830, 640, 885, GRN, "Continue")])
    an  = panel("and.png", crop=(0, 700, 1080, 1500), boxes=[(42, 1328, 1038, 1475, GRN, "Continue")])
    ios = panel("ios.png", crop=(0, 2000, 1206, 2622), boxes=[(485, 2140, 725, 2200, RED, "counter")])
    compose("out.png", [
        ("WEB", web, [(GRN, "matches the mock")]),
        ("ANDROID", an, [(GRN, "matches the mock")]),
        ("iOS", ios, [(RED, "counter shown (mock: none)")])])

Boxes are (x0, y0, x1, y1, colour, label) in the source image's pixels; an empty label draws the box only.
Colours: RED differs from the source of truth, GRN matches it, AMB a different pattern with no source.
Needs Pillow. Uses the first font found in FONTS, else Pillow's default.
"""
from PIL import Image, ImageDraw, ImageFont

FONTS = [("/System/Library/Fonts/Helvetica.ttc", 1), ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", None),
         ("C:/Windows/Fonts/arial.ttf", None)]  # (path, index of the bold face)
RED, GRN, AMB = (235, 64, 52), (46, 170, 100), (240, 170, 30)


def font(size, bold=False):
    for path, bold_index in FONTS:
        try:
            return ImageFont.truetype(path, size, index=bold_index if bold and bold_index else 0)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(d, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        if line and d.textlength(line + " " + word, font=fnt) > width:
            lines.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    return lines + [line]


def panel(path, crop, boxes, scale=1.0):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1, colour, label in boxes:
        x0, y0, x1, y1 = [v * scale for v in (x0, y0, x1, y1)]
        d.rectangle([x0, y0, x1, y1], outline=colour, width=max(4, im.width // 150))
        if not label:
            continue
        f = font(max(22, im.width // 28), True)
        tw, th = d.textlength(label, font=f), getattr(f, "size", 12) + 8
        left, top, right = crop[0] * scale, crop[1] * scale, min(crop[2] * scale, im.width)
        ty = y0 - th - 2 if y0 - th - 2 > top else y1 + 2
        tx = max(left + 4, min(x0, right - tw - 14))
        d.rectangle([tx, ty, tx + tw + 10, ty + th], fill=colour)
        d.text((tx + 5, ty + 2), label, font=f, fill="white")
    return im.crop([int(v * scale) for v in crop])


def compose(out, columns, width=420, pad=16, head=46):
    """columns: [(name, panel_image, [(colour, caption), ...]), ...]"""
    cap = font(17)
    panels = []
    for name, img, caps in columns:
        h = int(img.height * width / img.width)
        panels.append((name, img.resize((width, h), Image.LANCZOS), caps))
    maxh = max(p[1].height for p in panels)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    wrapped = [[(colour, wrap(probe, text, cap, width - 26)) for colour, text in caps] for _, _, caps in panels]
    cap_h = max(sum(22 * len(lines) + 8 for _, lines in w) for w in wrapped) + 20
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
        for colour, lines in wrapped[i]:
            d.ellipse([x, cy + 4, x + 16, cy + 20], fill=colour)
            for k, line in enumerate(lines):
                d.text((x + 24, cy + 22 * k), line, font=cap, fill=(30, 34, 42))
            cy += 22 * len(lines) + 8
    canvas.save(out, quality=88)
    return out
