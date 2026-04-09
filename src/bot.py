import os
import pyttsx3
import asyncio
import logging
import twitchio
import json

import sounddevice as sd
import soundfile as sf

from twitchio import eventsub
from twitchio.ext import commands
from dotenv import load_dotenv
from typing import Any

from events.tts import TextToSpeechEventHandler
load_dotenv()

LOGGER: logging.Logger = logging.getLogger(__name__)

class Bot(commands.Bot):

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.users_file = "tts_users.txt"
        self.tts_users = []
        self.tts_handler = TextToSpeechEventHandler()
        self.tts_queue = asyncio.Queue()
        asyncio.create_task(self.tts_worker())

        self.get_users()

    def get_users(self):
        data = self._load_json()

        if "names" in data:
            self.tts_users = data["names"]

    async def setup_hook(self) -> None:

        await self.setup_subscriptions()

        LOGGER.info("Finished setting up hooks")

    async def event_oauth_authorized(self, payload):
        await self.add_token(payload.access_token, payload.refresh_token)

    async def setup_subscriptions(self) -> None:
        chat = eventsub.ChatMessageSubscription(broadcaster_user_id=self.owner_id, user_id=self.bot_id)
        await self.subscribe_websocket(chat)

    async def event_message(self, payload):
        if "catch" in payload.text.lower():
            return
        
        if payload.source_broadcaster is not None:
            return

        if payload.chatter.name in self.tts_users:
            await self.tts_queue.put(payload)

        await self.process_commands(payload) 

    async def tts_worker(self):
        while True:
            payload = await self.tts_queue.get()
            await self.execute_tts(payload)
            self.tts_queue.task_done()

    async def event_ready(self) -> None:
        LOGGER.info("Logged in as: %s", self.user)

    async def execute_tts(self, payload: twitchio.ChatMessage):
        LOGGER.info("Execute TTS")
        message = payload.text
        self.tts_handler.speak(message)

    def _load_json(self):
        with open("env.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
