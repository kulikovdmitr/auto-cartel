import html
import json
import logging
import os
import urllib.request

log = logging.getLogger("autoservice.notify")


def send_telegram(text: str) -> None:
    token, chat = os.getenv("TG_BOT_TOKEN"), os.getenv("TG_CHAT_ID")
    if not token or not chat:
        return
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat, "text": text, "parse_mode": "HTML"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        log.exception("telegram notification failed")


def booking_text(record: dict, titles: list[str], currency: str) -> str:
    e = html.escape
    return "\n".join([
        "<b>Новая заявка</b>",
        f"Имя: {e(record['name'])}",
        f"Телефон: {e(record['phone'])}",
        f"Авто: {e(record['car'])}",
        f"Дата: {e(record['visit_date'] or 'не указана')}",
        "Услуги: " + e(", ".join(titles)),
        f"Итого: от {record['total_from']:,} {e(currency)}".replace(",", " "),
    ])