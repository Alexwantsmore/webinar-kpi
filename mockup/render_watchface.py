"""Render a watch face mockup for Garmin Fenix 7X Solar (280x280, round)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

W = H = 280
SCALE = 3
SW, SH = W * SCALE, H * SCALE

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def f(path, size):
    return ImageFont.truetype(path, size * SCALE)


def make_background():
    """Stylized sunset-Pula-Arena background placeholder."""
    img = Image.new("RGB", (SW, SH), (0, 0, 0))
    px = img.load()
    # Sky: blue top to warm orange bottom (golden hour)
    for y in range(SH):
        t = y / SH
        if t < 0.55:
            # Sky: deep blue to lighter blue
            k = t / 0.55
            r = int(40 + (130 - 40) * k)
            g = int(70 + (170 - 70) * k)
            b = int(130 + (200 - 130) * k)
        else:
            # Horizon to warm ground/arena light
            k = (t - 0.55) / 0.45
            r = int(200 + (150 - 200) * k)
            g = int(140 + (90 - 140) * k)
            b = int(90 + (40 - 90) * k)
        for x in range(SW):
            px[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img, "RGBA")

    # Suggest arena arches silhouette on the left/bottom
    arena_color = (90, 55, 30, 235)
    base_y = int(SH * 0.62)
    arch_h = int(SH * 0.22)
    arch_w = int(SW * 0.10)
    n_arches = 5
    start_x = -int(SW * 0.05)
    for i in range(n_arches):
        x0 = start_x + i * arch_w
        x1 = x0 + arch_w
        # Arch top
        draw.rectangle([x0, base_y, x1, SH], fill=arena_color)
        draw.pieslice([x0 - 2, base_y - arch_w // 2, x1 + 2, base_y + arch_w // 2],
                      180, 360, fill=arena_color)
        # cut window
        win_pad_x = int(arch_w * 0.25)
        win_pad_y = int(arch_h * 0.10)
        draw.rectangle([x0 + win_pad_x, base_y + win_pad_y, x1 - win_pad_x, SH],
                       fill=(180, 130, 80, 200))
        draw.pieslice([x0 + win_pad_x - 2, base_y - (arch_w - 2 * win_pad_x) // 2,
                       x1 - win_pad_x + 2, base_y + (arch_w - 2 * win_pad_x) // 2],
                      180, 360, fill=(180, 130, 80, 200))

    # Upper tier - smaller windows
    upper_y = int(SH * 0.40)
    upper_h = int(SH * 0.10)
    for i in range(n_arches):
        x0 = start_x + i * arch_w + arch_w // 4
        x1 = x0 + arch_w // 2
        draw.rectangle([x0, upper_y, x1, upper_y + upper_h], fill=arena_color)
        draw.rectangle([x0 + 4, upper_y + 4, x1 - 4, upper_y + upper_h - 4],
                       fill=(180, 130, 80, 200))

    img = img.filter(ImageFilter.GaussianBlur(radius=2))

    # Darken overlay so text reads well (essential for watch faces)
    overlay = Image.new("RGBA", (SW, SH), (0, 0, 0, 110))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    return img


def circular_mask(img):
    """Apply circular mask for round watch."""
    mask = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, SW, SH), fill=255)
    out = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def draw_text_shadow(draw, xy, text, font, fill=(255, 255, 255), anchor="mm"):
    x, y = xy
    # Soft shadow for legibility on busy backgrounds
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 200), anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def draw_arc_widget(draw, cx, cy, radius, value, max_value, color, bg=(255, 255, 255, 60)):
    """Draw a small circular progress arc."""
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    # background ring
    draw.arc(bbox, 0, 360, fill=bg, width=3 * SCALE)
    # progress
    angle = 360 * min(value / max_value, 1.0)
    draw.arc(bbox, -90, -90 + angle, fill=color, width=3 * SCALE)


def render():
    bg = make_background()
    img = circular_mask(bg)
    draw = ImageDraw.Draw(img, "RGBA")

    cx, cy = SW // 2, SH // 2

    # === CENTER: TIME (large) ===
    time_font = f(FONT_BOLD, 52)
    draw_text_shadow(draw, (cx, cy + 2 * SCALE), "08:42", time_font)

    # === DATE (above time) ===
    date_font = f(FONT_REG, 12)
    draw_text_shadow(draw, (cx, cy - 28 * SCALE), "PIĄ, 22 MAJ", date_font,
                     fill=(255, 220, 180))

    label_font = f(FONT_REG, 8)
    value_font = f(FONT_BOLD, 16)

    # === TOP (12): WOOCOMMERCE REVENUE (prominent) ===
    rx, ry = cx, int(SH * 0.13)
    draw_text_shadow(draw, (rx, ry - 10 * SCALE), "SKLEP · DZIŚ", label_font,
                     fill=(255, 215, 130))
    draw_text_shadow(draw, (rx, ry + 6 * SCALE), "1 247 zł",
                     f(FONT_BOLD, 18), fill=(255, 230, 160))
    # tiny bag icon to the left of the value
    bag_x = rx - 38 * SCALE
    bag_y = ry + 6 * SCALE
    draw.rectangle([bag_x - 5 * SCALE, bag_y - 4 * SCALE,
                    bag_x + 5 * SCALE, bag_y + 5 * SCALE],
                   fill=(255, 215, 130), outline=(0, 0, 0, 180), width=SCALE)
    draw.arc([bag_x - 3 * SCALE, bag_y - 7 * SCALE,
              bag_x + 3 * SCALE, bag_y - 2 * SCALE],
             180, 360, fill=(255, 215, 130), width=2 * SCALE)

    # === UPPER LEFT (~10): STRESS ===
    sx, sy = int(SW * 0.20), int(SH * 0.36)
    draw_arc_widget(draw, sx, sy, 13 * SCALE, 32, 100,
                    (255, 120, 80, 255))
    draw_text_shadow(draw, (sx, sy), "32", f(FONT_BOLD, 11))
    draw_text_shadow(draw, (sx, sy + 19 * SCALE), "STRES", label_font,
                     fill=(255, 200, 180))

    # === UPPER RIGHT (~2): TEMPERATURE ===
    tx, ty = int(SW * 0.80), int(SH * 0.36)
    draw_text_shadow(draw, (tx, ty - 5 * SCALE), "18°C",
                     f(FONT_BOLD, 15))
    # tiny sun icon above
    sun_x, sun_y = tx, ty - 18 * SCALE
    draw.ellipse([sun_x - 4 * SCALE, sun_y - 4 * SCALE,
                  sun_x + 4 * SCALE, sun_y + 4 * SCALE],
                 fill=(255, 200, 80))
    draw_text_shadow(draw, (tx, ty + 11 * SCALE), "POGODA", label_font,
                     fill=(255, 230, 200))

    # === LOWER LEFT (~8): BODY BATTERY ===
    bx, by = int(SW * 0.20), int(SH * 0.64)
    draw_arc_widget(draw, bx, by, 13 * SCALE, 68, 100,
                    (100, 200, 255, 255))
    draw_text_shadow(draw, (bx, by), "68", f(FONT_BOLD, 11))
    draw_text_shadow(draw, (bx, by + 19 * SCALE), "BODY BAT.", label_font,
                     fill=(180, 220, 255))

    # === LOWER RIGHT (~4): STEPS ===
    stx, sty = int(SW * 0.80), int(SH * 0.64)
    draw_arc_widget(draw, stx, sty, 13 * SCALE, 7234, 10000,
                    (120, 220, 140, 255))
    draw_text_shadow(draw, (stx, sty), "7.2k", f(FONT_BOLD, 10))
    draw_text_shadow(draw, (stx, sty + 19 * SCALE), "KROKI", label_font,
                     fill=(200, 255, 210))

    # === BOTTOM (6): SLEEP (time + score) ===
    slx, sly = cx, int(SH * 0.83)
    draw_text_shadow(draw, (slx, sly - 10 * SCALE), "SEN", label_font,
                     fill=(180, 200, 255))
    # time on left, score on right, separated by a thin divider
    draw_text_shadow(draw, (slx - 22 * SCALE, sly + 4 * SCALE),
                     "7h 23m", f(FONT_BOLD, 13))
    draw.line([(slx, sly - 3 * SCALE), (slx, sly + 11 * SCALE)],
              fill=(255, 255, 255, 120), width=SCALE)
    draw_text_shadow(draw, (slx + 22 * SCALE, sly + 4 * SCALE),
                     "84", f(FONT_BOLD, 14), fill=(180, 230, 255))
    draw_text_shadow(draw, (slx + 36 * SCALE, sly + 6 * SCALE),
                     "/100", f(FONT_REG, 8), fill=(200, 220, 255))

    # subtle bezel ring
    draw.ellipse([1, 1, SW - 1, SH - 1], outline=(255, 255, 255, 60),
                 width=2 * SCALE)
    # tick marks every 30deg
    for i in range(12):
        a = math.radians(i * 30 - 90)
        r1 = SW / 2 - 4 * SCALE
        r2 = SW / 2 - 10 * SCALE
        x1 = cx + r1 * math.cos(a)
        y1 = cy + r1 * math.sin(a)
        x2 = cx + r2 * math.cos(a)
        y2 = cy + r2 * math.sin(a)
        w = 2 * SCALE if i % 3 == 0 else 1 * SCALE
        draw.line([x1, y1, x2, y2], fill=(255, 255, 255, 140), width=w)

    # Downsample for AA quality at native 280x280
    out_native = img.resize((W, H), Image.LANCZOS)
    # Also a 2x large preview for visibility
    out_2x = img.resize((W * 2, H * 2), Image.LANCZOS)

    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    out_native.save(os.path.join(here, "watchface_280.png"))
    out_2x.save(os.path.join(here, "watchface_2x.png"))

    # Also: native + black bezel context, to show how it sits on real watch
    context_size = 420
    ctx = Image.new("RGB", (context_size, context_size), (15, 15, 18))
    cdraw = ImageDraw.Draw(ctx)
    # outer bezel
    cdraw.ellipse([10, 10, context_size - 10, context_size - 10],
                  fill=(35, 35, 38), outline=(80, 80, 85), width=3)
    cdraw.ellipse([30, 30, context_size - 30, context_size - 30],
                  fill=(10, 10, 12), outline=(60, 60, 65), width=2)
    inset = (context_size - W * 2) // 2
    ctx.paste(out_2x.convert("RGB"), (inset, inset),
              out_2x.split()[3] if out_2x.mode == "RGBA" else None)
    ctx.save(os.path.join(here, "watchface_on_watch.png"))

    print("Rendered:")
    print(" - watchface_280.png (native 280x280)")
    print(" - watchface_2x.png (560x560 preview)")
    print(" - watchface_on_watch.png (with bezel context)")


if __name__ == "__main__":
    render()
