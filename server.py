# -*- coding: utf-8 -*-
import http.server
import socketserver
import threading
import time
import os
import sys
from generate_obs_stats import generate_stats_json
from api_key_gui import APIKeyGUI, get_api_key_from_config

# Fix für Windows Console Encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PORT = 8080
GAME_NAME = "Piekasso"
TAG_LINE = "EUW"
API_KEY = get_api_key_from_config() or os.getenv("RIOT_API_KEY", "RGAPI-575f3234-c4e8-4dc9-91f4-3713a16f3f06")

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Handler mit CORS Support für lokales Development"""

    def end_headers(self):
        # CORS Headers hinzufügen
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def log_message(self, format, *args):
        # Nur wichtige Logs anzeigen
        if "stats.json" in args[0] or "obs_overlay.html" in args[0]:
            print(f"📡 Serve: {args[0]}")


def update_stats_loop():
    """Background-Thread der alle 60 Sekunden die Stats aktualisiert"""
    global API_KEY
    print(f"🔄 Stats-Updater gestartet (Update alle 60 Sekunden)")
    print(f"👤 Spieler: {GAME_NAME}#{TAG_LINE}\n")

    while True:
        try:
            print(f"⏳ Aktualisiere Stats... ({time.strftime('%H:%M:%S')})")
            success = generate_stats_json(GAME_NAME, TAG_LINE, API_KEY)

            if success:
                print(f"✅ Stats erfolgreich aktualisiert!\n")
            else:
                print(f"❌ Fehler beim Aktualisieren der Stats")
                print(f"💡 Öffne GUI für neuen API Key...\n")

                # Zeige GUI für neuen API Key
                gui = APIKeyGUI()
                new_key = gui.show()

                if new_key:
                    API_KEY = new_key
                    print(f"✅ Neuer API Key gespeichert! Versuche erneut...\n")
                    continue
                else:
                    print(f"⚠️ Kein neuer API Key eingegeben\n")

        except Exception as e:
            print(f"❌ Fehler: {e}\n")

        # Warte 60 Sekunden bis zum nächsten Update
        time.sleep(60)


def start_server():
    """Startet den HTTP Server"""
    global API_KEY

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    Handler = CORSRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 60)
        print("🎮 League of Legends OBS Overlay Server")
        print("=" * 60)
        print(f"🌐 Server läuft auf: http://localhost:{PORT}")
        print(f"📊 Overlay URL: http://localhost:{PORT}/obs_overlay.html")
        print(f"📁 Stats API: http://localhost:{PORT}/stats.json")
        print("-" * 60)
        print("⚙️  Einstellungen:")
        print(f"   Spieler: {GAME_NAME}#{TAG_LINE}")
        print(f"   Update-Intervall: 60 Sekunden")
        print("-" * 60)
        print("📝 OBS Setup:")
        print(f"   1. Öffne OBS Studio")
        print(f"   2. Füge 'Browser' Quelle hinzu")
        print(f"   3. URL: http://localhost:{PORT}/obs_overlay.html")
        print(f"   4. Breite: 520, Höhe: 450")
        print("-" * 60)
        print("🛑 Server stoppen: CTRL+C")
        print("=" * 60)
        print()

        # Generiere Stats beim Start
        print("🚀 Generiere initiale Stats...")
        success = generate_stats_json(GAME_NAME, TAG_LINE, API_KEY)

        # Wenn initial keine Daten empfangen, frage nach API Key
        if not success:
            print("❌ Keine Daten empfangen!")
            print("💡 Öffne GUI für API Key Eingabe...\n")

            gui = APIKeyGUI()
            new_key = gui.show()

            if new_key:
                API_KEY = new_key
                print("✅ Neuer API Key gespeichert! Versuche erneut...\n")
                success = generate_stats_json(GAME_NAME, TAG_LINE, API_KEY)

                if success:
                    print("✅ Stats erfolgreich generiert!\n")
                else:
                    print("⚠️ Immer noch Fehler - Server startet trotzdem\n")
            else:
                print("⚠️ Kein API Key eingegeben - Server startet trotzdem\n")
        else:
            print("✅ Bereit!\n")

        # Starte Background-Thread für Auto-Updates
        update_thread = threading.Thread(target=update_stats_loop, daemon=True)
        update_thread.start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server wird beendet...")
            print("✅ Erfolgreich gestoppt!")


if __name__ == "__main__":
    start_server()
