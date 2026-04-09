import tkinter as tk
from tkinter import ttk

import twitchio
from components.BotTab import BotTab
from components.TokenTab import TokenTab
from components.TTSTab import TTSTab
import logging
import os
LOGGER: logging.Logger = logging.getLogger(__name__)

class TwitchBotUI:
    def __init__(self, root):
        twitchio.utils.setup_logging(level=logging.INFO)
        self.root = root
        self.root.title("Rains Democracy Bot")
        self.root.geometry("600x500")
        self.root.iconbitmap("rains_slime.ico")

        self._create_tabs()

    def _create_tabs(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        self.token_tab = ttk.Frame(notebook)
        self.tts_tab = ttk.Frame(notebook)
        self.bot_tab = ttk.Frame(notebook)

        notebook.add(self.token_tab, text="Tokens")
        notebook.add(self.tts_tab, text="TTS")
        notebook.add(self.bot_tab, text="Bot")
        notebook.pack(expand = 1, fill ="both")

        self.token_view = TokenTab(self.token_tab)
        self.tts_view = TTSTab(self.tts_tab)
        self.bot_view = BotTab(self.bot_tab)

# ===== START =====
if __name__ == "__main__":
    if not os.path.exists("env.json"):
        with open("env.json", "w", encoding="utf-8") as f:
            f.write("{}")

    root = tk.Tk()
    app = TwitchBotUI(root)
    root.mainloop()