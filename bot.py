import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, balance, schedule, info

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


# ── Health check сервер ──────────────────────────────────────────────────────
# Render вимагає відкритий порт, а UptimeRobot пінгує його кожні 5 хв,
# щоб бот не засинав на безкоштовному плані.
async def health_handler(request):
    return web.Response(text="OK — EduBot is running 🤖")


async def run_web():
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    port = 8080
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Health check сервер запущено на порту {port} ✅")


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(schedule.router)
    dp.include_router(info.router)

    await run_web()

    logging.info("EduBot запущено ✅")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
