import os
import io
import logging
from dotenv import load_dotenv
from PIL import Image
from pathlib import Path        

from telegram import Update, InputSticker
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ───────────────────────────────
# StickerBot Class
# ───────────────────────────────

class StickerBot:
    MAX_STICKER_SIZE = 512
    DEFAULT_EMOJI = ["🔥"]

    def __init__(self):
        load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
        self.token = os.getenv("BOT_TOKEN")

        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=logging.INFO
        )

        self.startup_check()

        self.app = (
            Application.builder()
            .token(self.token)
            .post_init(self.verify_telegram_connection)
            .build()
        )

        self.bot_username = None

        self._register_handlers()


        
    #check for .env and token validity on startup
    def startup_check(self):
        env_path = Path(__file__).resolve().parent / ".env"

        # 1️⃣ Check .env existence
        if not env_path.exists():
            raise RuntimeError(
                f".env file not found at {env_path}\n"
                "Create a .env file with:\n"
                "BOT_TOKEN=your_token_here"
            )

        # 2️⃣ Check BOT_TOKEN presence
        if not self.token:
            raise RuntimeError(
                "BOT_TOKEN is missing.\n"
                "Check your .env file and ensure it contains:\n"
                "BOT_TOKEN=your_token_here"
            )

        # 3️⃣ Basic token sanity check
        if ":" not in self.token or len(self.token) < 40:
            raise RuntimeError(
                "BOT_TOKEN does not look valid.\n"
                "Did you paste the full token from @BotFather?"
            )

    # Verify Telegram connection and Username exists (Username is required for sticker pack creation)
    async def verify_telegram_connection(self, app):
        me = await app.bot.get_me()

        self.bot_username = me.username
        if not self.bot_username:
            raise RuntimeError("Failed to resolve bot username from Telegram")

        logging.info(f"🤖 Connected as @{self.bot_username}")


    # ───────────────────────────────
    # Setup
    # ───────────────────────────────

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

    async def _ensure_bot_username(self, context: ContextTypes.DEFAULT_TYPE):
        if not self.bot_username:
            me = await context.bot.get_me()
            self.bot_username = me.username

    # ───────────────────────────────
    # Commands
    # ───────────────────────────────

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 Send me an image and I’ll turn it into a sticker.\n"
            "Your personal sticker pack will be created automatically ✨"
        )

    # ───────────────────────────────
    # Core Logic
    # ───────────────────────────────

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type != "private":
            return

        await self._ensure_bot_username(context)

        user = update.message.from_user
        pack_name = self.get_pack_name(user.id)
        pack_title = f"{user.first_name}'s Stickers"

        sticker_file = await self.download_and_convert(update, context)
        sticker = self.make_input_sticker(sticker_file)

        if not await self.pack_exists(context, pack_name):
            await self.create_pack(context, user.id, pack_name, pack_title, sticker)
            await update.message.reply_text(
                "✨ Sticker pack created!\n"
                f"https://t.me/addstickers/{pack_name}"
            )
            return

        try:
            await self.add_sticker(context, user.id, pack_name, sticker)
            await update.message.reply_text(
                "✅ Sticker added!\n"
                f"https://t.me/addstickers/{pack_name}"
            )
        except Exception:
            await update.message.reply_text(
                "❌ Could not add sticker.\n"
                "Your sticker pack may be full."
            )

    # ───────────────────────────────
    # Sticker Pack Helpers
    # ───────────────────────────────

    def get_pack_name(self, user_id: int) -> str:
        return f"stickers_{user_id}_by_{self.bot_username}"

    async def pack_exists(self, context, pack_name: str) -> bool:
        try:
            await context.bot.get_sticker_set(pack_name)
            return True
        except:
            return False

    async def create_pack(self, context, user_id, pack_name, title, sticker):
        await context.bot.create_new_sticker_set(
            user_id=user_id,
            name=pack_name,
            title=title,
            stickers=[sticker]
        )

    async def add_sticker(self, context, user_id, pack_name, sticker):
        await context.bot.add_sticker_to_set(
            user_id=user_id,
            name=pack_name,
            sticker=sticker
        )

    # ───────────────────────────────
    # Image Processing
    # ───────────────────────────────

    async def download_and_convert(self, update, context) -> io.BytesIO:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()
        return self.image_to_sticker(image_bytes)

    def image_to_sticker(self, image_bytes: bytes) -> io.BytesIO:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        image.thumbnail((self.MAX_STICKER_SIZE, self.MAX_STICKER_SIZE), Image.LANCZOS)

        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        return output

    def make_input_sticker(self, sticker_file: io.BytesIO) -> InputSticker:
        return InputSticker(
            sticker=sticker_file,
            emoji_list=self.DEFAULT_EMOJI,
            format="static"   # required for PNG stickers
        )

    # ───────────────────────────────
    # Run
    # ───────────────────────────────

    def run(self):
        logging.info("Sticker bot running...")
        self.app.run_polling()


# ───────────────────────────────
# Entrypoint
# ───────────────────────────────

def main():
    bot = StickerBot()
    bot.run()

if __name__ == "__main__":
    main()




