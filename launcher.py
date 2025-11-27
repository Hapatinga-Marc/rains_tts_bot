import os
import sys
import json
import subprocess
import threading
import time

import dearpygui.dearpygui as dpg
import sounddevice as sd


HERE = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
BOT_PATH = os.path.join(HERE, "bot.py")

_proc = None
_proc_lock = threading.Lock()


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(values: dict):
    cfg = {
        "device": values.get("device", ""),
        "host": values.get("host", "localhost"),
        "port": values.get("port", "4455"),
        "password": values.get("password", "")
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)


def get_output_devices():
    try:
        devices = sd.query_devices()
        apis = sd.query_hostapis()
        api_names = {i: api["name"] for i, api in enumerate(apis)}

        # Nur Ausgabegeräte, mit API im Namen
        output_devices = [
            f"{d['name']} — {api_names[d['hostapi']]}"
            for d in devices
            if d.get("max_output_channels", 0) > 0
        ]
        return output_devices
    except Exception:
        return []


def _update_status(text: str):
    try:
        dpg_text = dpg.get_item(label="status_text") if False else None
    except Exception:
        dpg_text = None
    # DearPyGui update via set_value
    try:
        dpg.set_value("status_text", text)
    except Exception:
        pass


def _start_bot_cb(sender, app_data, user_data):
    global _proc
    with _proc_lock:
        if _proc and _proc.poll() is None:
            _update_status(f"Running (PID {_proc.pid})")
            return

        # read values from widgets
        device = dpg.get_value("device_combo")
        host = dpg.get_value("host_input")
        port = dpg.get_value("port_input")
        password = dpg.get_value("password_input")

        values = {"device": device, "host": host, "port": port, "password": password}
        save_config(values)

        try:
            _proc = subprocess.Popen([sys.executable, BOT_PATH], cwd=HERE)
            _update_status(f"Running (PID {_proc.pid})")
        except Exception as e:
            _update_status(f"Failed to start: {e}")


def _stop_bot_cb(sender, app_data, user_data):
    global _proc
    with _proc_lock:
        if _proc and _proc.poll() is None:
            _proc.terminate()
            try:
                _proc.wait(timeout=3)
            except Exception:
                _proc.kill()
            _update_status("Stopped")
            _proc = None
        else:
            _update_status("No running bot")


def _save_cb(sender, app_data, user_data):
    device = dpg.get_value("device_combo")
    host = dpg.get_value("host_input")
    port = dpg.get_value("port_input")
    password = dpg.get_value("password_input")
    values = {"device": device, "host": host, "port": port, "password": password}
    save_config(values)
    _update_status("Config saved")


def _device_changed(sender, app_data, user_data):
    """Callback for device combo - show full device name below the combo."""
    # app_data is the selected item (full device name from sounddevice)
    try:
        dpg.set_value("device_full", app_data)
    except Exception:
        pass


def _exit_cb(sender, app_data, user_data):
    # stop proc if needed and close GUI
    _stop_bot_cb(sender, app_data, user_data)
    dpg.stop_dearpygui()


def main():
    cfg = load_config() or {}
    output_devices = get_output_devices()
    default_device = output_devices[0] if output_devices else "(no devices)"

    dpg.create_context()
    dpg.create_viewport(title='TTS Bot Launcher', width=640, height=320)

    with dpg.window(label="TTS Bot Launcher", tag="main_window", width=620, height=300):
        with dpg.tab_bar(label="Tabs"):
            with dpg.tab(label="Settings"):
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=200)
                    dpg.add_text("Twitch configuration")
                    dpg.add_spacer(height=5)
                dpg.add_separator()
                dpg.add_spacer(height=5)
                dpg.add_text("Broadcaster client ID:")
                dpg.group()
                dpg.add_input_text(label="", default_value="", tag="broadcaster_client_id",width=400)
                dpg.add_spacer(height=5)
                dpg.add_text("Broadcaster seceret token:")
                dpg.group()
                dpg.add_input_text(label="", default_value="", tag="broadcaster_secret_token",width=400)
                dpg.add_spacer(height=5)
                dpg.add_text("Broadcaster ID:")
                dpg.group()
                dpg.add_input_text(label="", default_value="", tag="broadcaster_id",width=400)
                dpg.add_spacer(height=5)
                dpg.add_text("Bot ID:")
                dpg.group()
                dpg.add_input_text(label="", default_value="", tag="bot_id",width=400)
                dpg.add_spacer(height=5)
                dpg.add_separator()
                dpg.add_spacer(height=5)

                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=200)
                    dpg.add_text("TTS/Audio configuration:")
                
                dpg.add_spacer(height=5)

                with dpg.group():
                    dpg.add_text("Audio Output Device:")
                    dpg.add_combo(
                        output_devices if output_devices else ["(no devices)"],
                        default_value=cfg.get("device", "(no devices)"),
                        tag="device_combo",
                        width=500,
                        callback=_device_changed
                    )




                # dpg.add_text("🎧 Audio-Ausgabegerät:")
                # dpg.add_spacing(count=1)
                # dpg.add_combo(devices if devices else ["(no devices)"], default_value=cfg.get("device", devices[0] if devices else ""), tag="device_combo", width=10000, callback=_device_changed)
                # dpg.add_input_text(label="OBS Host", default_value=cfg.get("host", "localhost"), tag="host_input", width=300)
                # dpg.add_input_text(label="OBS Port", default_value=cfg.get("port", "4455"), tag="port_input", width=100)
                # dpg.add_input_text(label="OBS Passwort", default_value=cfg.get("password", ""), tag="password_input", password=True, width=300)
        dpg.add_separator()
        dpg.add_button(label="Save", callback=_save_cb)
        dpg.add_same_line()
        dpg.add_button(label="Save & Start", callback=_start_bot_cb, tag="start_btn")
        dpg.add_same_line()
        dpg.add_button(label="Stop", callback=_stop_bot_cb, tag="stop_btn")
        dpg.add_same_line()
        dpg.add_button(label="Exit", callback=_exit_cb)
        dpg.add_spacing(count=2)
        dpg.add_text("Status: Stopped", tag="status_text")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
