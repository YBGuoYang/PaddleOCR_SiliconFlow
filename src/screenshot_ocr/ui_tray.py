"""System tray helpers for the current desktop app."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont


def create_tray_icon_image(width: int = 64, height: int = 64) -> Image.Image:
    image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    def round_rectangle(xy, radius, fill):
        x1, y1, x2, y2 = xy
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)

    round_rectangle([4, 4, 60, 60], 12, fill=(65, 105, 225))

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 24)
        except OSError:
            font = ImageFont.load_default()

    text = "OCR"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 2
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    draw.rectangle([8, 50, 16, 54], fill=(255, 255, 255))
    return image


def create_tray_icon(on_screenshot, on_settings, on_exit, *, icon_name: str = "screenshot_ocr", title: str = "截图OCR工具"):
    import pystray

    menu = pystray.Menu(
        pystray.MenuItem("📷 截图 OCR", on_screenshot, default=True),
        pystray.MenuItem("⚙️ 设置", on_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ 退出", on_exit),
    )
    return pystray.Icon(icon_name, create_tray_icon_image(), title, menu)
