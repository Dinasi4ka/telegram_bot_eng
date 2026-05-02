"""
Google Sheets service.

ОДИН файл (BotData) з двома листами:

Users:
  A: phone  | B: name | C: paid | D: used

Schedule:
  A: date   | B: time | C: is_booked | D: booked_by_phone
"""

import json
import os
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from config import (
    GOOGLE_CREDENTIALS_JSON,
    SPREADSHEET_ID,
    SHEET_USERS,
    SHEET_SCHEDULE
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ───────────────────────── CLIENT ─────────────────────────

def _get_client() -> gspread.Client:
    """Авторизація в Google Sheets."""
    creds_data = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if creds_data and creds_data.strip().startswith("{"):
        info = json.loads(creds_data)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_JSON,
            scopes=SCOPES
        )

    return gspread.authorize(creds)


def _open_sheet(sheet_name: str) -> gspread.Worksheet:
    """Відкриває конкретний лист (tab) з таблиці."""
    client = _get_client()
    return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)


# ───────────────────────── USERS ─────────────────────────

def get_user_by_phone(phone: str) -> Optional[dict]:
    ws = _open_sheet(SHEET_USERS)
    records = ws.get_all_records()

    phone_clean = _normalize_phone(phone)

    for i, row in enumerate(records, start=2):
        if _normalize_phone(str(row.get("phone", ""))) == phone_clean:
            return {"row": i, **row}

    return None


def add_user(phone: str, name: str) -> bool:
    """Додає нового користувача."""
    ws = _open_sheet(SHEET_USERS)

    ws.append_row([
        phone,
        name,
        "",   # paid
        0     # used
    ])

    return True


def increment_used(phone: str) -> bool:
    user = get_user_by_phone(phone)

    if not user:
        return False

    ws = _open_sheet(SHEET_USERS)

    new_val = int(user.get("used", 0)) + 1
    ws.update_cell(user["row"], 4, new_val)

    return True


def get_all_users() -> list[dict]:
    ws = _open_sheet(SHEET_USERS)
    return ws.get_all_records()


# ───────────────────────── SCHEDULE ─────────────────────────

def get_free_slots() -> list[dict]:
    ws = _open_sheet(SHEET_SCHEDULE)
    records = ws.get_all_records()

    free = []

    for i, row in enumerate(records, start=2):
        booked = str(row.get("is_booked", "")).strip().lower()

        if booked not in ("true", "1", "так", "yes", "+"):
            free.append({"row": i, **row})

    return free


def book_slot(row_index: int, phone: str) -> bool:
    ws = _open_sheet(SHEET_SCHEDULE)

    ws.update_cell(row_index, 3, "TRUE")
    ws.update_cell(row_index, 4, phone)

    return True


def unbook_slot_by_phone_and_slot(date: str, time: str, phone: str) -> bool:
    ws = _open_sheet(SHEET_SCHEDULE)
    records = ws.get_all_records()

    for i, row in enumerate(records, start=2):
        if (
            str(row.get("date", "")) == date
            and str(row.get("time", "")) == time
            and _normalize_phone(str(row.get("booked_by_phone", ""))) == _normalize_phone(phone)
        ):
            ws.update_cell(i, 3, "")
            ws.update_cell(i, 4, "")
            return True

    return False


def get_booked_slots_by_phone(phone: str) -> list[dict]:
    ws = _open_sheet(SHEET_SCHEDULE)
    records = ws.get_all_records()

    phone_clean = _normalize_phone(phone)

    result = []

    for i, row in enumerate(records, start=2):
        if _normalize_phone(str(row.get("booked_by_phone", ""))) == phone_clean:
            result.append({"row": i, **row})

    return result


# ───────────────────────── HELPERS ─────────────────────────

def _normalize_phone(phone: str) -> str:
    """Приводить номер до формату 0XXXXXXXXX (наприклад: 0978514337)."""
    import re

    if not phone:
        return ""

    # прибираємо все зайве (пробіли, +, -, дужки)
    phone = re.sub(r"[^\d]", "", phone)

    # якщо формат +380XXXXXXXXX або 380XXXXXXXXX
    if phone.startswith("380"):
        phone = "0" + phone[3:]

    return phone
