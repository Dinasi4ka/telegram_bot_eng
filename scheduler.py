import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from services.sheets import _open_sheet
from config import SHEET_SCHEDULE, SHEET_USERS

logger = logging.getLogger(__name__)


def _normalize_phone(phone: str) -> str:
    import re
    digits = re.sub(r"[^\d]", "", str(phone))
    if len(digits) == 12 and digits.startswith("380"):
        return digits[3:]
    if len(digits) == 10 and digits.startswith("0"):
        return digits[1:]
    return digits


async def check_and_send_reminders(bot: Bot):
    try:
        now = datetime.now()
        target = now + timedelta(hours=1, minutes=30)
        target_date = target.strftime("%Y-%m-%d")
        target_time = target.strftime("%H:%M")

        schedule_ws = _open_sheet(SHEET_SCHEDULE)
        users_ws = _open_sheet(SHEET_USERS)

        lessons = schedule_ws.get_all_records()
        users = users_ws.get_all_records()

        for lesson in lessons:
            booked = str(lesson.get("is_booked", "")).strip().lower()
            if booked not in ("true", "1", "так", "yes", "+"):
                continue

            if str(lesson.get("date", "")) != target_date:
                continue
            if str(lesson.get("time", "")) != target_time:
                continue

            phone = str(lesson.get("booked_by_phone", ""))
            phone_clean = _normalize_phone(phone)

            for user in users:
                if _normalize_phone(str(user.get("phone", ""))) == phone_clean:
                    tg_id = user.get("telegram_id")
                    if tg_id:
                        try:
                            await bot.send_message(
                                int(tg_id),
                                f"⏰ <b>Нагадування про заняття!</b>\n\n"
                                f"📆 Сьогодні о <b>{lesson['time']}</b>\n\n"
                                f"Не забудьте підготуватись! 📚",
                                parse_mode="HTML"
                            )
                            logger.info(f"Нагадування надіслано: {user.get('name')} ({tg_id})")
                        except Exception as e:
                            logger.error(f"Не вдалось надіслати {tg_id}: {e}")
                    break

    except Exception as e:
        logger.error(f"Помилка планувальника: {e}")


def start_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_and_send_reminders,
        trigger="interval",
        minutes=10,
        args=[bot],
        next_run_time=datetime.now()
    )
    scheduler.start()
    logger.info("Планувальник нагадувань запущено ✅")
    return scheduler