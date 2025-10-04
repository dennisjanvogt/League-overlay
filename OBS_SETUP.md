# 🎮 League of Legends OBS Overlay - Setup Guide

Ein ansprechendes Live-Stats Overlay für OBS mit Grafiken, Champion-Bildern und Echtzeit-Updates!

## ✨ Features

- 🏆 **Ranked Statistiken** (Tier, Rank, LP, Winrate)
- 👤 **Spieler-Profil** mit Icon und Level
- 🎯 **Top 3 Champions** mit Mastery und Punkten
- 🖼️ **Grafiken & Icons** direkt von der Riot API
- 🔄 **Auto-Refresh** alle 60 Sekunden
- 🎨 **Modernes Design** mit Gold-Akzenten und Glassmorphismus

---

## 📋 Voraussetzungen

1. **Python 3.7+** installiert
2. **Riot API Key** von [developer.riotgames.com](https://developer.riotgames.com/)
3. **OBS Studio** installiert
4. **requests** Bibliothek: `pip install requests`

---

## 🚀 Schnellstart

### Schritt 1: API Key einrichten

Setze deinen Riot API Key als Umgebungsvariable:

**Windows (CMD):**
```cmd
set RIOT_API_KEY=dein-api-key-hier
```

**Windows (PowerShell):**
```powershell
$env:RIOT_API_KEY="dein-api-key-hier"
```

**Alternative:** Trage den Key direkt in `generate_obs_stats.py` ein (Zeile 197)

---

### Schritt 2: Stats generieren

**Einmaliger Run:**
```bash
python generate_obs_stats.py
```

**Live-Modus (empfohlen für Streams):**
```bash
python generate_obs_stats.py --live
```

Der Live-Modus aktualisiert die Stats automatisch alle 60 Sekunden!

---

### Schritt 3: OBS einrichten

1. **Öffne OBS Studio**
2. **Füge eine neue Quelle hinzu:**
   - Klicke auf `+` unter "Quellen"
   - Wähle **"Browser"**
   - Name: "League Stats Overlay"

3. **Konfiguration:**
   - ✅ **Lokal**: Aktiviert
   - **Lokale Datei**:
     ```
     C:\Users\dejaw\Desktop\Claude Code SDK\obs_overlay.html
     ```
   - **Breite**: `450`
   - **Höhe**: `400`
   - ✅ **Quelle neuladen, wenn Szene aktiv wird**: Aktiviert
   - **CSS anpassen** (optional):
     ```css
     body { background: transparent; }
     ```

4. **Position anpassen:**
   - Ziehe das Overlay an die gewünschte Position
   - Empfehlung: Unten links oder rechts

---

## 🎨 Anpassungen

### Spieler ändern

Bearbeite in `generate_obs_stats.py` (Zeile 202-203):
```python
GAME_NAME = "DeinName"
TAG_LINE = "EUW"
```

### Update-Intervall ändern

Im Live-Modus (Zeile 230):
```python
run_continuous(60)  # Sekunden zwischen Updates
```

### Design anpassen

Bearbeite `obs_overlay.html`:
- **Farben**: Suche nach `#c89b3c` (Gold) und ändere sie
- **Größe**: Passe `.overlay-container width` an
- **Schriftart**: Ändere `font-family` in den Styles

---

## 📁 Dateien

| Datei | Beschreibung |
|-------|-------------|
| `league.py` | Haupt-Script zum Abrufen von League Daten |
| `generate_obs_stats.py` | Generiert `stats.json` für OBS Overlay |
| `obs_overlay.html` | HTML/CSS Overlay für OBS Browser Source |
| `stats.json` | Generierte Stats (wird automatisch erstellt) |

---

## 🎯 Verwendung während des Streams

### Empfohlener Workflow:

1. **Vor dem Stream:**
   ```bash
   python generate_obs_stats.py --live
   ```
   Lasse das Script im Hintergrund laufen!

2. **OBS Szene aktivieren:**
   - Das Overlay wird automatisch geladen
   - Stats werden alle 60 Sekunden aktualisiert

3. **Nach dem Stream:**
   - Drücke `Ctrl+C` im Terminal, um das Script zu beenden

---

## 🐛 Troubleshooting

### Overlay zeigt "Lade Statistiken..."
- ✅ Prüfe, ob `stats.json` existiert
- ✅ Führe `python generate_obs_stats.py` aus

### Bilder werden nicht angezeigt
- ✅ Prüfe deine Internetverbindung
- ✅ Data Dragon API muss erreichbar sein

### "API Key nicht gesetzt" Fehler
- ✅ Setze `RIOT_API_KEY` Umgebungsvariable
- ✅ Oder trage den Key direkt im Script ein

### OBS zeigt leere Seite
- ✅ Prüfe den Dateipfad in der Browser-Quelle
- ✅ Aktiviere "Quelle neuladen" in OBS
- ✅ Öffne die Entwicklertools in OBS (Rechtsklick → "Mit Browser interagieren")

---

## 🎨 Beispiel-Screenshot

Das Overlay zeigt:
```
┌─────────────────────────────────────┐
│  [Icon]  Piekasso#EUW               │
│          Level 122                  │
├─────────────────────────────────────┤
│  [Rank Icon]  GOLD II               │
│               45 LP                 │
│  Siege: 120  Niederlagen: 95        │
│  Winrate: 55.8%                     │
├─────────────────────────────────────┤
│  TOP CHAMPIONS                      │
│  [Yasuo]  [Zed]  [Akali]           │
│   M7       M7      M6               │
│   250K     180K    120K             │
└─────────────────────────────────────┘
```

---

## 💡 Tipps & Tricks

1. **Performance:** Der Live-Modus nutzt minimal Ressourcen
2. **Rate Limits:** Riot API hat Rate Limits - 60s Updates sind sicher
3. **Szenen:** Erstelle mehrere OBS-Szenen mit verschiedenen Overlays
4. **Chroma Key:** Der Hintergrund ist transparent - perfekt für Overlays!

---

## 📞 Support

Bei Problemen:
1. Prüfe die Riot API Status: [status.riotgames.com](https://status.riotgames.com/)
2. Validiere deinen API Key: [developer.riotgames.com](https://developer.riotgames.com/)
3. Teste das Overlay im Browser: Öffne `obs_overlay.html` direkt

---

## 🎉 Viel Erfolg beim Streamen!

Erstellt mit ❤️ für die League of Legends Community
