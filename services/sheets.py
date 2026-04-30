import json
import os
import re
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from config import (
    GOOGLE_CREDENTIALS_JSON,
    SPREADSHEET_ID,
    SHEET_USERS,
    SHEET_SCHEDULE,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ───────────────────────── CLIENT ─────────────────────────
def _get_client() -> gspread.Client:
    creds_data = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if creds_data and creds_data.strip().startswith("{"):
        info = json.loads(creds_data)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_JSON,
            scopes=SCOPES,
        )

    return gspread.authorize(creds)


def _get_spreadsheet():
    client = _get_client()
    return client.open_by_key(SPREADSHEET_ID)


# ───────────────────────── USERS ─────────────────────────
def _users_ws():
    return _get_spreadsheet().worksheet(SHEET_USERS)


def get_user_by_phone(phone: str) -> Optional[dict]:
    ws = _users_ws()
    records = ws.get_all_records()

    phone_clean = _normalize(phone)

    for i, row in enumerate(records, start=2):
        if _normalize(str(row.get("phone", ""))) == phone_clean:
            return {"row": i, **row}

    return None


def increment_used(phone: str) -> bool:
    user = get_user_by_phone(phone)
    if not user:
        return False

    ws = _users_ws()
    new_val = int(user.get("used", 0)) + 1
    ws.update_cell(user["row"], 4, new_val)
    return True


def get_all_users():
    return _users_ws().get_all_records()


# ───────────────────────── SCHEDULE ─────────────────────────
def _schedule_ws():
    return _get_spreadsheet().worksheet(SHEET_SCHEDULE)


def get_free_slots():
    ws = _schedule_ws()
    records = ws.get_all_records()

    free = []
    for i, row in enumerate(records, start=2):
        booked = str(row.get("is_booked", "")).strip().lower()
        if booked not in ("true", "1", "так", "yes", "+"):
            free.append({"row": i, **row})

    return free


def book_slot(row_index: int, phone: str) -> bool:
    ws = _schedule_ws()
    ws.update_cell(row_index, 3, "TRUE")
    ws.update_cell(row_index, 4, phone)
    return True


def unbook_slot(date: str, time: str, phone: str) -> bool:
    ws = _schedule_ws()
    records = ws.get_all_records()

    for i, row in enumerate(records, start=2):
        if (
            str(row.get("date", "")) == date
            and str(row.get("time", "")) == time
            and _normalize(str(row.get("booked_by_phone", ""))) == _normalize(phone)
        ):
            ws.update_cell(i, 3, "")
            ws.update_cell(i, 4, "")
            return True

    return False


def get_booked_slots_by_phone(phone: str):
    ws = _schedule_ws()
    records = ws.get_all_records()

    phone_clean = _normalize(phone)

    result = []
    for i, row in enumerate(records, start=2):
        if _normalize(str(row.get("booked_by_phone", ""))) == phone_clean:
            result.append({"row": i, **row})

    return result


# ───────────────────────── HELPERS ─────────────────────────
def _normalize(phone: str) -> str:
    return re.sub(r"[\s\(\)\-]", "", phone)