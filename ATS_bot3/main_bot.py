# main_bot.py async version
import logging
import asyncio

from Config import Config
from telegram_client import TelegramClient
from startup_validator import StartupValidator
from handlers import BotHandlers
from sticker_serviceV2 import StickerService


class MainBot:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=logging.INFO
        )

        # Configuration and app
        self.config = Config()
        self.client = TelegramClient(self.config.bot_token)
        self.app = self.client.get_app()

        # Validators and services
        self.validator = StartupValidator(self.app)
        self.sticker_service = StickerService(self.app)

        # Handlers
        self.handlers = BotHandlers(self.app, self.sticker_service)
        self.handlers.register()
        
        # Run startup validation BEFORE polling
        self.app.post_init = self.post_init

    async def post_init(self, app):
        await self.validator.verify_connection()
        
    def run(self):
        logging.info("Bot is running...")
        self.app.run_polling()



# main entry point
if __name__ == "__main__":
    bot = MainBot()
    bot.run()