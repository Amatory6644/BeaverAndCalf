"""Send the latest comic and its caption to a Telegram chat."""

import os
import sys
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parent.parent
IMAGE_PATH = ROOT / "content" / "latest.jpg"
CAPTION_PATH = ROOT / "content" / "caption.txt"


def main() -> int:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    missing = [name for name, value in (("TELEGRAM_BOT_TOKEN", token), ("TELEGRAM_CHAT_ID", chat_id)) if not value]
    if missing:
        print(f"Ошибка: не заданы переменные окружения: {', '.join(missing)}", file=sys.stderr)
        return 1
    if not IMAGE_PATH.is_file():
        print(f"Ошибка: изображение не найдено: {IMAGE_PATH}", file=sys.stderr)
        return 1
    if not CAPTION_PATH.is_file():
        print(f"Ошибка: подпись не найдена: {CAPTION_PATH}", file=sys.stderr)
        return 1

    caption = CAPTION_PATH.read_text(encoding="utf-8").strip()
    if not caption:
        print("Ошибка: content/caption.txt пуст.", file=sys.stderr)
        return 1

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        with IMAGE_PATH.open("rb") as image:
            response = requests.post(
                url,
                data={"chat_id": chat_id, "caption": caption},
                files={"photo": (IMAGE_PATH.name, image, "image/jpeg")},
                timeout=60,
            )
        try:
            result = response.json()
        except ValueError:
            print(f"Ошибка: Telegram вернул HTTP {response.status_code} и некорректный JSON.", file=sys.stderr)
            return 1

        if not response.ok or not result.get("ok"):
            description = result.get("description", "неизвестная ошибка Telegram")
            print(f"Ошибка Telegram Bot API: {description}", file=sys.stderr)
            return 1

    except requests.RequestException as exc:
        print(f"Ошибка сети при отправке изображения в Telegram: {exc}", file=sys.stderr)
        return 1

    print("Комикс успешно отправлен в Telegram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
