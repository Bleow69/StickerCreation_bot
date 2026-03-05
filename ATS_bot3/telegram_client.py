# telegram_client.py

from telegram.ext import Application

class TelegramClient:
    def __init__(self, token: str):
        self.app = Application.builder().token(token).build()

    def get_app(self):
        return self.app



# ───────────────────────────────
# Add .post_init(...)
# Add rate limiter
# Add custom defaults
# Switch polling → webhook
# Inject proxy
# Add connection pool config
# ───────────────────────────────

# class TelegramClient:
#     def __init__(self, token: str):
#         self.app = (
#             Application.builder()
#             .token(token)
#             .post_init(self._post_init)
#             .build()
#         )

#     async def _post_init(self, app):
#         logging.info("Telegram client initialized")

#     def get_app(self):
#         return self.app
