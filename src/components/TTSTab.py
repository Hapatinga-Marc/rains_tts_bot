import os
import logging
import json

import sounddevice as sd
import soundfile as sf
import tkinter as tk

from tkinter import ttk

LOGGER: logging.Logger = logging.getLogger(__name__)

class TTSTab():

    def __init__(self, frame):
        self.tts_tab = frame
        self.tts_users = []
        self.tts_users_file = "tts_users.txt"
        self.sound_devices = self._get_sound_devices()
        self.app_device_idx = self._load_audio_device()
        self._build_tab()
        self._load_users()  
    
    def _build_tab(self):
        audio_frame = ttk.LabelFrame(self.tts_tab, text="Audio devices")
        audio_frame.pack(fill="x", padx=10, pady=10)

        device_names = [device['name'] for device in self.sound_devices]
        self.audio_combo = ttk.Combobox(audio_frame, values=device_names, state="readonly")
        self.audio_combo.pack(fill="x", padx=5, pady=5)

        if device_names:
            self.audio_combo.current(self.app_device_idx)

        frame = ttk.LabelFrame(self.tts_tab, text="TTS Users")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", pady=5)

        self.user_entry = ttk.Entry(input_frame)
        self.user_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        ttk.Button(input_frame, text="Add", command=self.add_user)\
            .grid(row=1, column=1)

        input_frame.columnconfigure(0, weight=1)

        # Enter = hinzufügen
        self.user_entry.bind("<Return>", lambda e: self.add_user())

        self.user_listbox = tk.Listbox(frame)
        self.user_listbox.pack(fill="both", expand=True)

        ttk.Button(frame, text="Remove", command=self.remove_user).pack(pady=5)

        self.user_listbox.bind("<Delete>", lambda e: self.remove_user())
        self.audio_combo.bind("<<ComboboxSelected>>", lambda e: self._on_device_selected())

    def _load_users(self):
        data = self._load_json()

        if "names" not in data:
            data["names"] = []

        for name in data["names"]:
            self.tts_users.append(name)
            self.user_listbox.insert(tk.END, name)

    def _load_audio_device(self):
        data = self._load_json()

        if "audio_device" in data:
            if "app_index" in data["audio_device"]:
                return data["audio_device"]["app_index"]
            else:
                return 0

    def _save_users(self):
        data = self._load_json()
        data["names"] = self.tts_users

        with open("env.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def add_user(self):
        username = self.user_entry.get().strip()
        if username and username not in self.tts_users:
            self.tts_users.append(username)
            self.user_listbox.insert(tk.END, username)
            self.user_entry.delete(0, tk.END)
            self._save_users() 

    def remove_user(self):
        selected = self.user_listbox.curselection()
        if not selected:
            return

        index = selected[0]
        username = self.user_listbox.get(index)

        self.tts_users.remove(username)
        self.user_listbox.delete(index)
        self._save_users()

    def _get_sound_devices(self):
        devices = sd.query_devices()
        output_devices = [d for d in devices if d['hostapi'] == 1]
        return output_devices
    
    def _on_device_selected(self):
        data = self._load_json()
        selected_index = self.audio_combo.current()

        if "audio_device" not in data:
            data["audio_device"] = {}

        if selected_index >= 0:
            data["audio_device"] = self.sound_devices[selected_index]
            data["audio_device"]["app_index"] = selected_index
            self._save_selected_device(data)
            LOGGER.info(f"Selected audio device: {data['audio_device']['name']} (ID: {data['audio_device']['index']})")

    def _save_selected_device(self, device):
        with open("env.json", "w", encoding="utf-8") as f:
            json.dump(device, f, indent=4)

    def _load_json(self):
        with open("env.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data