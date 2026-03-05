# startup_validator.py

import logging

class StartupValidator:
    def __init__(self, app):
        self.app = app

    async def verify_connection(self):
        """
        Verifies that the bot can connect to Telegram and has a username.
        """
        try:
            bot_info = await self.app.bot.get_me()  # synchronous call
            if not bot_info.username:
                raise RuntimeError("Bot username not set in BotFather")
            logging.info(f"Connected as @{bot_info.username}")
        except Exception:
            logging.exception("Failed to connect to Telegram")
            raise
