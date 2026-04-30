import os
from dotenv import load_dotenv

load_dotenv()

# ───────────────────────── BOT ─────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

ADMIN_IDS: list[int] = list(
    map(int, os.getenv("ADMIN_IDS", "0").split(","))
)

# ───────────────────────── GOOGLE ─────────────────────────
GOOGLE_CREDENTIALS_JSON: str = os.getenv(
    "GOOGLE_CREDENTIALS_JSON",
    "credentials.json"
)

# 🔥 ОДИН СПІЛЬНИЙ GOOGLE SHEET (BotData)
SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")

# ───────────────────────── SHEETS (tabs) ─────────────────────────
SHEET_USERS: str = "Users"
SHEET_SCHEDULE: str = "Schedule"

# ───────────────────────── CENTER INFO ─────────────────────────
CENTER_NAME: str = "EduBot Навчальний Центр"
CENTER_PHONE: str = "+380 44 123-45-67"
CENTER_ADDRESS: str = "вул. Навчальна, 12"
CENTER_SCHEDULE: str = "Пн–Пт: 09:00–20:00, Сб: 09:00–16:00"