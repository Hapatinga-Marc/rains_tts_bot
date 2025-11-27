# TTS Bot Launcher

Kleine GUI zum Konfigurieren und Starten des TTS-Bots.

Features
- Auswahl des Audio-Ausgabegeräts
- Eingabe von OBS-Websocket Host/Port/Passwort
- Speichern der Einstellungen in `config.json`
- Starten/Stoppen von `bot.py` als Subprozess

Voraussetzungen
- Windows (getestet)
- Python 3.8+

Installation
1. Erstelle eine virtuelle Umgebung (empfohlen):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Installiere Abhängigkeiten:

```powershell
python -m pip install -r requirements.txt
```

Benutzung
1. Starte den Launcher (DearPyGui-Frontend):

```powershell
python launcher.py
```

2. Wähle das gewünschte Audio-Gerät und trage bei Bedarf OBS-Infos ein.
3. Klicke auf „Save & Start“, um `config.json` zu schreiben und `bot.py` zu starten.

Hinweis
- `bot.py` bleibt unverändert; der Launcher startet es als eigenen Prozess.
