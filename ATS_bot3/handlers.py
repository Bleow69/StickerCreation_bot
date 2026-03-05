# handlers.py (For routing commands and calls)

from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from sticker_serviceV2 import StickerService



class BotHandlers:
    def __init__(self, app, sticker_service: StickerService):
        """
        app: telegram.ext.Application instance
        sticker_service: StickerService instance
        """
        self.app = app
        self.sticker_service = sticker_service

    def register(self):
        """Register all handlers to the bot."""
        # Command handler for /start
        sticker_conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("sticker", self.sticker_service.start)
            ],

            states={
                    StickerService.PHOTO_STEP: [
                        MessageHandler(filters.PHOTO, self.sticker_service.ask_for_emoji)
                    ],

                    StickerService.EMOJI_STEP: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.sticker_service.receive_emoji)
                    ],
                    
                    ConversationHandler.TIMEOUT: [
                        MessageHandler(filters.ALL, self.sticker_service.timeout)
                    ],
                },

            fallbacks=[
                    CommandHandler("cancel", self.sticker_service.cancel)
                ],
            )

        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(sticker_conv_handler)
        
    # async handler for /start
    async def start(self, update, context):
        await update.message.reply_text("Sticker bot is running!")
