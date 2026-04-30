import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS: list[int] = list(map(int, os.getenv("ADMIN_IDS", "0").split(",")))

# Google Sheets
GOOGLE_CREDENTIALS_JSON: str = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")
SPREADSHEET_ID_USERS: str    = os.getenv("SPREADSHEET_ID_USERS", "")
SPREADSHEET_ID_SCHEDULE: str = os.getenv("SPREADSHEET_ID_SCHEDULE", "")

SHEET_USERS    = "Users"     # phone | name | paid | used
SHEET_SCHEDULE = "Schedule"  # date  | time | is_booked | booked_by_phone

CENTER_NAME     = "EduBot Навчальний Центр"
CENTER_PHONE    = "+380 44 123-45-67"
CENTER_ADDRESS  = "вул. Навчальна, 12"
CENTER_SCHEDULE = "Пн–Пт: 09:00–20:00, Сб: 09:00–16:00"
