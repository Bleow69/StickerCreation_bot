# sticker_service.py

from telegram import InputSticker
from telegram.error import TelegramError
from image_processor import ImageProcessor
from telegram.ext import ConversationHandler
import emoji

class StickerService:
    PHOTO_STEP = 0
    EMOJI_STEP = 1
    
    def __init__(self, app):
        self.app = app
        self.image_processor = ImageProcessor()

    async def start(self, update, context):
        await update.message.reply_text(
        "📸 Please send the photo you want to turn into a sticker."
    )
        return self.PHOTO_STEP

        
    def is_valid_single_emoji(self, text: str) -> bool:
        if not text:
            return False

        text = text.strip()

        # Extract emojis from the text
        emojis = emoji.emoji_list(text)

        # Must contain exactly one emoji
        if len(emojis) != 1:
            return False

        # That emoji must be the entire message (no extra text)
        return emojis[0]["emoji"] == text



    async def ask_for_emoji(self, update, context):
        if update.message.chat.type != "private":
            return

        # Store photo file_id in user context
        photo = update.message.photo[-1]
        context.user_data["photo_file_id"] = photo.file_id

        await update.message.reply_text(
            "Please send an emoji that represents this sticker 😊"
        )

        return self.EMOJI_STEP 

    #limit to one emoji with no text 
    async def receive_emoji(self, update, context):
        
        # Handle timeout or non-text responses
        if update.message.text is None:
            await update.message.reply_text("❌ Timeout or invalid input.")
            return ConversationHandler.END
                
        emoji = update.message.text.strip()

        if not self.is_valid_single_emoji(emoji):
            await update.message.reply_text(
                "❌ Please send exactly ONE emoji (example: 🔥)"
            )
            return self.EMOJI_STEP

        #Retrieve stored photo file_id
        file_id = context.user_data.get("photo_file_id")
        if not file_id:
            await update.message.reply_text("Something went wrong. Please send the photo again.")
            return ConversationHandler.END

        user = update.message.from_user
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username

        pack_name = f"stickers_{user.id}_by_{bot_username}"
        pack_title = f"{user.first_name}'s Stickers"

        file = await context.bot.get_file(file_id)

        self.image_processor.validate_input_size(file.file_size)
        image_bytes = await file.download_as_bytearray()

        try:
            processed_image = self.image_processor.process_image(image_bytes)
        except ValueError as e:
            await update.message.reply_text(str(e))
            return ConversationHandler.END

        sticker = InputSticker(
            sticker=processed_image,
            emoji_list=[emoji],
            format="static"
        )

        if not await self.pack_exists(pack_name):
            await self.create_pack(user.id, pack_name, pack_title, sticker)

            await update.message.reply_text(
                f"✨ Sticker pack created!\n"
                f"https://t.me/addstickers/{pack_name}"
            )
        else:
            await self.add_sticker(user.id, pack_name, sticker)

            await update.message.reply_text(
                f"✅ Sticker added!\n"
                f"https://t.me/addstickers/{pack_name}"
            )

        return ConversationHandler.END

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

    async def timeout(self, update, context):
        if update.message:
            await update.message.reply_text(
                "⏳ Session expired. Please start again with /sticker."
            )

        # Clear stored data just in case
        context.user_data.clear()

        return ConversationHandler.END