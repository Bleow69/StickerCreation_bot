# config.py

import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self):
        env_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(env_path)

        self.bot_token = os.getenv("BOT_TOKEN")

        if not self.bot_token:
            raise RuntimeError("BOT_TOKEN not found in .env")
