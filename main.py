import asyncio
import logging
from datetime import datetime
from pyrogram import Client
from pyrogram.enums import ParseMode
from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, PORT, OWNER_ID
import pyrogram.utils
from aiohttp import web

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

name = """
🤖 Crunchyroll Link Provider Started
🎬 Protecting Anime Channels from Copyright Issues
🔗 Temporary Links with Auto-Revocation
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="CrunchyrollBot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
            sleep_threshold=60,
        )
        self.LOGGER = LOGGER
        self.start_time = None
        self.username = None

    async def start(self, *args, **kwargs):
        await super().start()
        usr_bot_me = await self.get_me()
        self.start_time = datetime.now()
        self.username = usr_bot_me.username

        # Notify owner
        try:
            await self.send_message(
                chat_id=OWNER_ID,
                text="<b>🤖 <blockquote>Crunchyroll Link Provider Started Successfully!</blockquote></b>\n"
                     f"<b>⏰ Started at:</b> {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                     f"<b>👤 Username:</b> @{self.username}",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            self.LOGGER.warning(f"Failed to notify owner: {e}")

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER.info("="*50)
        self.LOGGER.info(name)
        self.LOGGER.info(f"Bot: @{self.username}")
        self.LOGGER.info(f"Owner: {OWNER_ID}")
        self.LOGGER.info("="*50)

        # Start web server for potential webhooks
        try:
            app = web.Application()
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", PORT)
            await site.start()
            self.LOGGER.info(f"Web server started on port {PORT}")
        except Exception as e:
            self.LOGGER.error(f"Web server error: {e}")

        # Start background tasks
        asyncio.create_task(self.background_tasks())

    async def background_tasks(self):
        """Run background maintenance tasks"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                # Clean expired data, check system health, etc.
                pass
            except Exception as e:
                self.LOGGER.error(f"Background task error: {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER.info("Bot stopped gracefully")

if __name__ == "__main__":
    # Create bot instance
    bot = Bot()
    
    # Run bot
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.LOGGER.info("Bot stopped by user")
    except Exception as e:
        bot.LOGGER.error(f"Bot crashed: {e}")
