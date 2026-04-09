import os
import pyttsx3
import asyncio
import logging
import twitchio
import json

import sounddevice as sd
import soundfile as sf

LOGGER: logging.Logger = logging.getLogger(__name__)

class TextToSpeechEventHandler:
    def __init__(self):
        self.device_index = self.get_audio_output()
        self.output_wav = "tts_output.wav"

    def get_audio_output(self):
        data = self._load_json()

        if "audio_device" in data:
            return data["audio_device"]["index"]
        else:
            return None

    def speak(self, text: str):
        """Generiert neue WAV-Datei, löscht alte und spielt sie ab."""
        try:
            if os.path.exists(self.output_wav):
                os.remove(self.output_wav)
                LOGGER.info("Deleted old WAV file.")

            LOGGER.info("Generating new TTS file...")
            engine = pyttsx3.init()
            engine.save_to_file(text, self.output_wav)
            engine.runAndWait()
            engine.stop()

            LOGGER.info("Playing TTS...")
            data, samplerate = sf.read(self.output_wav)
            sd.play(data, samplerate, device=self.device_index)
            sd.wait()
            LOGGER.info("Finished playback.")

        except Exception as e:
            LOGGER.error("Error in _speak(): %s", e, exc_info=True)

    def _load_json(self):
        with open("env.json", "r", encoding="utf-8") as f:
            return json.load(f)