from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_IMG = PROJECT_ROOT / "static" / "img"
APP_ASSETS = PROJECT_ROOT / "mac_app_assets"
ICONSET = APP_ASSETS / "AI_Music_Recommender.iconset"


def font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_gradient(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), "#07111f")
    pixels = image.load()
    for y in range(size):
        for x in range(size):
            dx = x / size
            dy = y / size
            teal = max(0, 1 - math.hypot(dx - 0.72, dy - 0.25) * 1.8)
            violet = max(0, 1 - math.hypot(dx - 0.2, dy - 0.85) * 1.6)
            r = int(7 + teal * 22 + violet * 54)
            g = int(17 + teal * 120 + violet * 22)
            b = int(31 + teal * 92 + violet * 98)
            pixels[x, y] = (r, g, b, 255)
    return image


def rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    return mask


def generate_icon(size: int = 1024) -> Image.Image:
    base = make_gradient(size)
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_glow = ImageDraw.Draw(glow)
    draw_glow.ellipse((120, 120, size - 120, size - 120), fill=(52, 255, 129, 42))
    draw_glow.ellipse((260, 260, size - 260, size - 260), fill=(116, 255, 86, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(size // 15))
    base.alpha_composite(glow)

    draw = ImageDraw.Draw(base)
    margin = size * 0.12
    disc_box = (margin, margin, size - margin, size - margin)
    draw.ellipse(disc_box, fill=(10, 20, 35, 226), outline=(113, 255, 121, 120), width=max(6, size // 80))

    for i in range(8):
        inset = margin + i * size * 0.038
        alpha = max(20, 92 - i * 9)
        draw.ellipse((inset, inset, size - inset, size - inset), outline=(180, 255, 210, alpha), width=max(2, size // 220))

    center = size // 2
    center_radius = size * 0.105
    draw.ellipse(
        (center - center_radius, center - center_radius, center + center_radius, center + center_radius),
        fill=(239, 255, 247, 245),
    )
    draw.ellipse(
        (center - center_radius * 0.4, center - center_radius * 0.4, center + center_radius * 0.4, center + center_radius * 0.4),
        fill=(8, 18, 30, 255),
    )

    wave_color = (117, 255, 92, 230)
    for i, height in enumerate([0.16, 0.26, 0.38, 0.52, 0.34, 0.22, 0.42]):
        x = size * (0.28 + i * 0.07)
        y1 = size * (0.62 - height / 2)
        y2 = size * (0.62 + height / 2)
        draw.rounded_rectangle((x, y1, x + size * 0.035, y2), radius=size * 0.02, fill=wave_color)

    node_color = (182, 255, 220, 238)
    points = [
        (size * 0.33, size * 0.34),
        (size * 0.52, size * 0.25),
        (size * 0.67, size * 0.38),
        (size * 0.58, size * 0.52),
    ]
    for start, end in zip(points, points[1:]):
        draw.line((*start, *end), fill=(182, 255, 220, 120), width=max(3, size // 120))
    for x, y in points:
        r = size * 0.024
        draw.ellipse((x - r, y - r, x + r, y + r), fill=node_color)

    draw.text((size * 0.34, size * 0.73), "AI", font=font(size // 6), fill=(245, 255, 250, 245))
    draw.text((size * 0.55, size * 0.735), "♪", font=font(size // 7), fill=(117, 255, 92, 245))

    mask = rounded_mask(size, size // 5)
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(base, (0, 0), mask)
    return output


def save_iconset(icon: Image.Image) -> None:
    ICONSET.mkdir(parents=True, exist_ok=True)
    sizes = {
        "icon_16x16.png": 16,
        "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32,
        "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128,
        "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256,
        "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512,
        "icon_512x512@2x.png": 1024,
    }
    for name, size in sizes.items():
        icon.resize((size, size), Image.Resampling.LANCZOS).save(ICONSET / name)


def main() -> None:
    STATIC_IMG.mkdir(parents=True, exist_ok=True)
    APP_ASSETS.mkdir(parents=True, exist_ok=True)
    icon = generate_icon()
    icon.save(STATIC_IMG / "logo.png")
    icon.resize((192, 192), Image.Resampling.LANCZOS).save(STATIC_IMG / "logo-192.png")
    icon.save(
        APP_ASSETS / "AI_Music_Recommender.icns",
        format="ICNS",
        sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)],
    )
    save_iconset(icon)


if __name__ == "__main__":
    main()
