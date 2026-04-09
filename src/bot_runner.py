import os
import pyttsx3
import asyncio
import threading
import logging
import twitchio
import json

import sounddevice as sd
import soundfile as sf

from twitchio import eventsub
from twitchio.ext import commands
from dotenv import load_dotenv
from typing import Any

from bot import Bot
load_dotenv()

LOGGER: logging.Logger = logging.getLogger(__name__)

class BotRunner:
    def __init__(self):
        self.loop = None
        self.thread = None
        self.bot = None
        self.client_id = None
        self.client_secret = None
        self.user_id = None
        self.bot_id = None

    def start_bot(self):
        self._set_tokens()
        if self.thread and self.thread.is_alive():
            LOGGER.warning("Bot is already running")
            return
        LOGGER.info("Starting bot...")
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_bot, daemon=True)
        self.thread.start()

    def stop_bot(self):
        if self.loop and self.bot:
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._shutdown_bot())
            )
    
    def _run_bot(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.runner())

    def _load_tokens(self):
        try:
            with open("env.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data['tokens']
        except FileNotFoundError:
            return {}
        
    def _set_tokens(self):
        tokens = self._load_tokens()
        self.client_id = tokens['client_id']
        self.client_secret = tokens['client_secret']
        self.user_id = tokens['user_id']
        self.bot_id = tokens['bot_id']

    async def _shutdown_bot(self):
        await self.bot.close()

    async def runner(self):

        async with Bot(
            client_id=self.client_id,
            client_secret=self.client_secret,
            bot_id=self.bot_id,
            owner_id=self.user_id,
            prefix="!",
        ) as bot:
            self.bot = bot
            await bot.start()