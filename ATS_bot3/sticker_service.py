# sticker_service.py (async version)

from telegram import InputSticker
from telegram.error import TelegramError
from image_processor import ImageProcessor


class StickerService:
    DEFAULT_EMOJI = ["🔥"]
    EMOJI_TIMEOUT = 60  # seconds to wait for user emoji response

    def __init__(self, app):
        self.app = app
        self.image_processor = ImageProcessor()

    async def handle_photo(self, update, context):
        if update.message.chat.type != "private":
            return

        user = update.message.from_user

        # get bot username (async)
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username

        pack_name = f"stickers_{user.id}_by_{bot_username}"
        pack_title = f"{user.first_name}'s Stickers"

        photo = update.message.photo[-1]

        # Get file (async)
        file = await context.bot.get_file(photo.file_id)

        # Validate file size
        self.image_processor.validate_input_size(file.file_size)

        # Download file (async)
        image_bytes = await file.download_as_bytearray()

        # Process image safely
        try:
            processed_image = self.image_processor.process_image(image_bytes)
        except ValueError as e:
            await update.message.reply_text(str(e))
            return

        # Create InputSticker
        sticker = InputSticker(
            sticker=processed_image,
            emoji_list=self.DEFAULT_EMOJI,
            format="static"
        )

        # Check if pack exists
        if not await self.pack_exists(pack_name):
            await self.create_pack(user.id, pack_name, pack_title, sticker)

            await update.message.reply_text(
                f"✨ Sticker pack created!\n"
                f"https://t.me/addstickers/{pack_name}"
            )
            return

        # Add to existing pack
        await self.add_sticker(user.id, pack_name, sticker)

        await update.message.reply_text(
            f"✅ Sticker added!\n"
            f"https://t.me/addstickers/{pack_name}"
        )

    async def pack_exists(self, pack_name: str) -> bool:
        try:
            await self.app.bot.get_sticker_set(pack_name)
            return True
        except TelegramError:
            return False

    async def create_pack(self, user_id, pack_name, title, sticker):
        await self.app.bot.create_new_sticker_set(
            user_id=user_id,
            name=pack_name,
            title=title,
            stickers=[sticker]
        )

    async def add_sticker(self, user_id, pack_name, sticker):
        await self.app.bot.add_sticker_to_set(
            user_id=user_id,
            name=pack_name,
            sticker=sticker
        )
