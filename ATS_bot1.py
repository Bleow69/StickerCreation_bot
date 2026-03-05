import os
import io
import logging
from PIL import Image
from telegram import InputSticker
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ───────────────────────────────
# Setup
# ───────────────────────────────

#load_dotenv(dotenv_path=".env")

BOT_TOKEN = "8310381601:AAHyDeepsbSkT2dh6biwqXvZHqGQep3lO-Y"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

MAX_STICKER_SIZE = 512

# ───────────────────────────────
# Helpers
# ───────────────────────────────

def build_pack_name(user_id: int, bot_username: str) -> str:
    return f"stickers_{user_id}_by_{bot_username}"

def build_pack_title(first_name: str) -> str:
    return f"{first_name}'s Stickers"

def image_to_sticker(image_bytes: bytes) -> io.BytesIO:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    image.thumbnail((MAX_STICKER_SIZE, MAX_STICKER_SIZE), Image.LANCZOS)

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

# ───────────────────────────────
# Commands
# ───────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me any image and I’ll turn it into a sticker.\n\n"
        "Each user gets their own sticker pack automatically ✨"
    )

# ───────────────────────────────
# Main Photo Handler (DM only)
# ───────────────────────────────

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat = message.chat

    # Only allow private chats
    if chat.type != "private":
        return

    user = message.from_user
    bot = context.bot
    bot_username = (await bot.get_me()).username

    pack_name = build_pack_name(user.id, bot_username)
    pack_title = build_pack_title(user.first_name or "User")

    # Get highest resolution photo
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()

    sticker_file = image_to_sticker(image_bytes)

    # Try to get sticker pack
    pack_exists = True
    try:
        await bot.get_sticker_set(pack_name)
    except:
        pack_exists = False

    # Create pack if it doesn't exist
    if not pack_exists:
        sticker = InputSticker(
            sticker=sticker_file,
            emoji_list=["🔥"]
        )

        await bot.create_new_sticker_set(
            user_id=user.id,
            name=pack_name,
            title=pack_title,
            stickers=[sticker]
        )

        await message.reply_text(
            "✨ Sticker pack created!\n"
            f"https://t.me/addstickers/{pack_name}"
        )
        return

    # Add sticker to existing pack
    try:
        sticker = InputSticker(
            sticker=sticker_file,
            emoji_list=["🔥"]
        )

        await bot.add_sticker_to_set(
            user_id=user.id,
            name=pack_name,
            sticker=sticker
        )


        await message.reply_text(
            "✅ Sticker added!\n"
            f"https://t.me/addstickers/{pack_name}"
        )

    except Exception as e:
        await message.reply_text(
            "❌ Could not add sticker.\n"
            "Your sticker pack may be full (max ~120 stickers)."
        )

# ───────────────────────────────
# Run Bot
# ───────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logging.info("Sticker bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
