from bot import Bot

import logging

LOGGER: logging.Logger = logging.getLogger(__name__)

class EventMessages():
    def __init__(self, bot: Bot):
        self.bot = bot

    async def handle_message(self, payload):
        if "catch" in payload.text.lower():
            return
        
        if payload.source_broadcaster is not None:
            return

        if payload.chatter.name == "hawkmah":
            LOGGER.info("Test")
            await self.bot.execute_tts(payload)

        await self.bot.process_commands(payload)

        