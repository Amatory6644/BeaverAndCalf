"""Render and send the latest beaver-and-calf comic to Telegram."""

import os
import sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = ROOT / "content" / "latest.svg"
JPG_PATH = ROOT / "content" / "latest.jpg"
RENDERED_PATH = ROOT / "content" / "rendered_latest.png"
CAPTION_PATH = ROOT / "content" / "caption.txt"

def prepare_image():
    if SVG_PATH.is_file():
        try:
            import cairosvg
        except ImportError:
            print("Ошибка: CairoSVG не установлен.", file=sys.stderr)
            return None, None
        cairosvg.svg2png(
            url=str(SVG_PATH),
            write_to=str(RENDERED_PATH),
            output_width=1080,
            output_height=1440,
        )
        return RENDERED_PATH, "image/png"
    if JPG_PATH.is_file():
        return JPG_PATH, "image/jpeg"
    print("Ошибка: content/latest.svg или content/latest.jpg не найден.", file=sys.stderr)
    return None, None

def main() -> int:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    missing = [n for n,v in (("TELEGRAM_BOT_TOKEN",token),("TELEGRAM_CHAT_ID",chat_id)) if not v]
    if missing:
        print(f"Ошибка: не заданы переменные окружения: {', '.join(missing)}", file=sys.stderr)
        return 1
    if not CAPTION_PATH.is_file():
        print("Ошибка: content/caption.txt не найден.", file=sys.stderr)
        return 1

    image_path, mime = prepare_image()
    if not image_path:
        return 1

    caption = CAPTION_PATH.read_text(encoding="utf-8").strip()
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        with image_path.open("rb") as image:
            response = requests.post(
                url,
                data={"chat_id": chat_id, "caption": caption},
                files={"photo": (image_path.name, image, mime)},
                timeout=60,
            )
        result = response.json()
        if not response.ok or not result.get("ok"):
            print(f"Ошибка Telegram Bot API: {result.get('description','неизвестная ошибка')}", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"Ошибка отправки: {exc}", file=sys.stderr)
        return 1

    print("Комикс успешно отправлен в Telegram.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
