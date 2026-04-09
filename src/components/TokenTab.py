from tkinter import ttk

import json

class TokenTab():
    def __init__(self, frame):
        self.token_tab = frame
        self.build_token_tab()

    def build_token_tab(self):
        frame = ttk.LabelFrame(self.token_tab, text="Twitch Tokens")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Client ID").grid(row=0, column=0, sticky="w")
        self.client_id = ttk.Entry(frame, width=40)
        self.client_id.grid(row=0, column=1, pady=5)
        ttk.Button(frame, text="Update", command=lambda: self._update_env("client_id"))\
            .grid(row=0, column=2, padx=5)

        ttk.Label(frame, text="Client Secret").grid(row=1, column=0, sticky="w")
        self.client_secret = ttk.Entry(frame, width=40)
        self.client_secret.grid(row=1, column=1, pady=5)
        ttk.Button(frame, text="Update", command=lambda: self._update_env("client_secret"))\
            .grid(row=1, column=2, padx=5)

        ttk.Label(frame, text="User ID").grid(row=2, column=0, sticky="w")
        self.user_id = ttk.Entry(frame, width=40)
        self.user_id.grid(row=2, column=1, pady=5)
        ttk.Button(frame, text="Update", command=lambda: self._update_env("user_id"))\
            .grid(row=2, column=2, padx=5)

        ttk.Label(frame, text="Bot ID").grid(row=3, column=0, sticky="w")
        self.bot_id = ttk.Entry(frame, width=40)
        self.bot_id.grid(row=3, column=1, pady=5)
        ttk.Button(frame, text="Update", command=lambda: self._update_env("bot_id"))\
            .grid(row=3, column=2, padx=5)
        
        self._insert_saved_tokens()
        
    def _insert_saved_tokens(self):
        data = self._load_json()

        if "tokens" not in data:
            return
        else:
            self.client_id.insert(0, data["tokens"].get("client_id", ""))
            self.client_secret.insert(0, data["tokens"].get("client_secret", ""))
            self.user_id.insert(0, data["tokens"].get("user_id", ""))
            self.bot_id.insert(0, data["tokens"].get("bot_id", ""))

    def _update_env(self, key=None):
        data = self._load_json()

        if "tokens" not in data:
            data["tokens"] = {}

        if key == "client_id":
            data["tokens"]["client_id"] = self.client_id.get()
        elif key == "client_secret":
            data["tokens"]["client_secret"] = self.client_secret.get()
        elif key == "user_id":
            data["tokens"]["user_id"] = self.user_id.get()
        elif key == "bot_id":
            data["tokens"]["bot_id"] = self.bot_id.get()

        self._save_json(data)

    def _load_json(self):
        try:
            with open("env.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return {"tokens": {}}
        
    def _save_json(self, data):
        with open("env.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)