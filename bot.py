import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update

from config import BOT_TOKEN
from handlers import start, balance, schedule, info

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

BASE_URL = "https://telegram-bot-eng-stpt.onrender.com"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = BASE_URL + WEBHOOK_PATH


async def health_handler(request):
    return web.Response(text="OK — EduBot is running 🤖")


async def webhook_handler(request):
    bot = request.app["bot"]
    dp = request.app["dp"]

    data = await request.json()
    update = Update.model_validate(data)

    await dp.feed_update(bot, update)

    return web.Response(text="OK")


async def run_web(app):
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))  # 🔥 FIX FOR RENDER
    site = web.TCPSite(runner, "0.0.0.0", port)

    await site.start()
    logging.info(f"Web server запущено на порту {port} ✅")


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(schedule.router)
    dp.include_router(info.router)

    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp

    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_post(WEBHOOK_PATH, webhook_handler)

    await run_web(app)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

    logging.info(f"Webhook встановлено: {WEBHOOK_URL} ✅")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())