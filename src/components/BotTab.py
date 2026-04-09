import sys
import logging

import tkinter as tk

from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from bot_runner import BotRunner

class BotTab():
    def __init__(self, frame):
        self.bot_runner = BotRunner()
        self.bot_tab = frame
        self.build_bot_tab()

    def build_bot_tab(self):
        frame = ttk.LabelFrame(self.bot_tab, text="Bot Steuerung")
        frame.pack(fill="x", padx=10, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        start_btn = ttk.Button(button_frame, text="▶ Start", padding=3, command=lambda: self.bot_runner.start_bot())
        stop_btn = ttk.Button(button_frame, text="⏹ Stop", padding=3, command=lambda: self.bot_runner.stop_bot())

        start_btn.grid(row=0, column=0, sticky="ew", padx=3, pady=3)
        stop_btn.grid(row=0, column=1, sticky="ew", padx=3, pady=3)

        button_frame.columnconfigure(0, weight=1, uniform="buttons")
        button_frame.columnconfigure(1, weight=1, uniform="buttons")


