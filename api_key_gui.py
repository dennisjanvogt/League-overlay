# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import json
import os

class APIKeyGUI:
    """GUI zur Eingabe eines neuen API Keys"""

    def __init__(self):
        self.api_key = None
        self.window = None

    def show(self) -> str:
        """Zeigt das GUI-Fenster und gibt den eingegebenen API Key zurück"""
        self.window = tk.Tk()
        self.window.title("Riot API Key erforderlich")
        self.window.geometry("500x200")
        self.window.resizable(False, False)

        # Zentriere das Fenster
        self.window.eval('tk::PlaceWindow . center')

        # Überschrift
        header = tk.Label(
            self.window,
            text="⚠️ Keine Daten erhalten - API Key erforderlich",
            font=("Arial", 12, "bold"),
            fg="#d32f2f"
        )
        header.pack(pady=15)

        # Info-Text
        info = tk.Label(
            self.window,
            text="Der aktuelle API Key ist ungültig oder abgelaufen.\nBitte gib einen neuen Riot API Key ein:",
            font=("Arial", 9),
            justify="center"
        )
        info.pack(pady=5)

        # API Key Eingabefeld
        self.entry = tk.Entry(self.window, width=50, font=("Courier", 10))
        self.entry.pack(pady=10, padx=20)
        self.entry.focus()

        # Link zum API Key Portal
        link_text = tk.Label(
            self.window,
            text="API Key hier erstellen: https://developer.riotgames.com/",
            font=("Arial", 8),
            fg="#1976d2",
            cursor="hand2"
        )
        link_text.pack(pady=5)

        # Button Frame
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=15)

        # Speichern Button
        save_btn = tk.Button(
            btn_frame,
            text="Speichern",
            command=self._save_key,
            bg="#4caf50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        # Abbrechen Button
        cancel_btn = tk.Button(
            btn_frame,
            text="Abbrechen",
            command=self._cancel,
            bg="#757575",
            fg="white",
            font=("Arial", 10),
            width=12,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # Enter-Taste zum Speichern
        self.entry.bind('<Return>', lambda e: self._save_key())

        # Fenster modal machen
        self.window.grab_set()
        self.window.mainloop()

        return self.api_key

    def _save_key(self):
        """Speichert den eingegebenen API Key"""
        key = self.entry.get().strip()

        if not key:
            messagebox.showwarning("Warnung", "Bitte gib einen API Key ein!")
            return

        if not key.startswith("RGAPI-"):
            response = messagebox.askyesno(
                "Ungültiges Format",
                "Der API Key hat nicht das erwartete Format (RGAPI-...).\nTrotzdem fortfahren?"
            )
            if not response:
                return

        self.api_key = key
        self._save_to_config(key)
        self.window.destroy()

    def _cancel(self):
        """Bricht die Eingabe ab"""
        self.api_key = None
        self.window.destroy()

    def _save_to_config(self, api_key: str):
        """Speichert den API Key in einer config.json Datei"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")

        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                pass

        config['api_key'] = api_key

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)


def get_api_key_from_config() -> str:
    """Liest den API Key aus der config.json oder Umgebungsvariable"""
    # Erst aus config.json versuchen
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'api_key' in config:
                    return config['api_key']
        except:
            pass

    # Fallback auf Umgebungsvariable
    return os.getenv("RIOT_API_KEY", "")


if __name__ == "__main__":
    # Test
    gui = APIKeyGUI()
    key = gui.show()
    if key:
        print(f"API Key gespeichert: {key[:20]}...")
    else:
        print("Abgebrochen")
