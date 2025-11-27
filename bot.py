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
load_dotenv()

LOGGER: logging.Logger = logging.getLogger(__name__)

OUTPUT_WAV = "tts_output.wav"
OUTPUT_DEVICE = ""

USER_ID = os.getenv("TWITCH_USER_ID")
BOT_ID = os.getenv("BOT_ID")
BOT_CLIENT_ID = os.getenv("BOT_CLIENT_ID")
BOT_SECRET = os.getenv("BOT_SECRET")
BOT_ACCESS_TOKEN=os.getenv("BOT_ACCESS_TOKEN")
BOT_REFRESH_TOKEN=os.getenv("BOT_REFRESH_TOKEN")

class Bot(commands.Bot):

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.device_name = OUTPUT_DEVICE

    async def setup_hook(self) -> None:
        await self.add_token(BOT_ACCESS_TOKEN, BOT_REFRESH_TOKEN)

        await self.setup_subscriptions()

        LOGGER.info("Finished setting up hooks")

    async def event_oauth_authorized(self, payload):
        await self.add_token(payload.access_token, payload.refresh_token)

    async def setup_subscriptions(self) -> None:
        chat = eventsub.ChatMessageSubscription(broadcaster_user_id=self.owner_id, user_id=BOT_ID)
        await self.subscribe_websocket(chat)

    async def event_message(self, payload):
        if "catch" in payload.text.lower():
            return
        
        if payload.source_broadcaster is not None:
            return
        
        # Add new users here to allow TTS

        if payload.chatter.name == "hawkmah":
            LOGGER.info("Test")
            await self.execute_tts(payload)

        await self.process_commands(payload)


    async def event_ready(self) -> None:
        LOGGER.info("Logged in as: %s", self.user)

    async def execute_tts(self, payload: twitchio.ChatMessage):
        LOGGER.info("Execute TTS")
        message = payload.text
        self._speak(message)

    def _tts_filter(self, text: str) -> None:
        """Filtert unerwünschte Wörter aus dem Text heraus."""
        
        # Beispiel-Implementierung: Ersetze bestimmte Wörter
        banned_words = ["badword1", "badword2"]
        for word in banned_words:
            text = text.replace(word, "***")
        return text


    def _speak(self, text: str):
        """Generiert neue WAV-Datei, löscht alte und spielt sie ab."""
        try:
            if os.path.exists(OUTPUT_WAV):
                os.remove(OUTPUT_WAV)
                LOGGER.info("Deleted old WAV file.")

            LOGGER.info("Generating new TTS file...")
            engine = pyttsx3.init()
            engine.save_to_file(text, OUTPUT_WAV)
            engine.runAndWait()
            engine.stop()

            LOGGER.info("Playing TTS...")
            data, samplerate = sf.read(OUTPUT_WAV)
            sd.play(data, samplerate, device=self.device_name)
            sd.wait()
            LOGGER.info("Finished playback.")

        except Exception as e:
            LOGGER.error("Error in _speak(): %s", e, exc_info=True)

def get_audio_output() -> list[str]:
    """Gibt eine Liste aller verfügbaren Audio-Ausgabegeräte zurück."""
    try:
        devices = sd.query_devices()
        output_devices = [
            d['name']
            for d in devices
            if d.get("max_output_channels", 0) > 0
        ]
        return output_devices
    except Exception as e:
        LOGGER.error("Error getting audio output devices: %s", e, exc_info=True)
        return []
        
def main() -> None:
    twitchio.utils.setup_logging(level=logging.INFO)

    LOGGER.info(f"All available audio output devices: {get_audio_output()}")

    async def runner() -> None:
        async with Bot(
            client_id=BOT_CLIENT_ID,
            client_secret=BOT_SECRET,
            bot_id=BOT_ID,
            owner_id=USER_ID,
            prefix="!"
        ) as bot:
            await bot.start()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt")

if __name__ == "__main__":
    main()
