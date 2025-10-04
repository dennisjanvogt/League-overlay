# -*- coding: utf-8 -*-
import requests
import os
import json
import time
import sys
from typing import Dict, List, Optional

# Fix für Windows Console Encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class DataDragonAPI:
    """Client für Data Dragon API (Champion Bilder, Icons, etc.)"""

    def __init__(self):
        # Hole die neueste Version
        self.version = self.get_latest_version()
        self.base_url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}"

    def get_latest_version(self) -> str:
        """Holt die neueste Version von Data Dragon"""
        url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(url)
        if response.status_code == 200:
            versions = response.json()
            return versions[0]
        return "13.24.1"  # Fallback

    def get_champion_data(self) -> Dict:
        """Holt alle Champion-Daten"""
        url = f"{self.base_url}/data/de_DE/champion.json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return {}

    def get_champion_icon_url(self, champion_name: str) -> str:
        """Generiert die URL für ein Champion-Icon"""
        return f"{self.base_url}/img/champion/{champion_name}.png"

    def get_profile_icon_url(self, icon_id: int) -> str:
        """Generiert die URL für ein Profil-Icon"""
        return f"{self.base_url}/img/profileicon/{icon_id}.png"

    def get_champion_name_by_id(self, champion_id: int, champion_data: Dict) -> str:
        """Konvertiert Champion ID zu Namen"""
        for champ_key, champ_info in champion_data.get("data", {}).items():
            if int(champ_info.get("key", 0)) == champion_id:
                return champ_key
        return "Unknown"


class RiotAPI:
    """Client für die Riot Games API um League of Legends Daten abzurufen"""

    def __init__(self, api_key: str, region: str = "europe"):
        self.api_key = api_key
        self.region = region
        self.platform = "euw1"
        self.base_url_regional = f"https://{self.region}.api.riotgames.com"
        self.base_url_platform = f"https://{self.platform}.api.riotgames.com"
        self.headers = {"X-Riot-Token": self.api_key}

    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """Holt Account-Informationen basierend auf Riot ID"""
        url = f"{self.base_url_regional}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_summoner_by_puuid(self, puuid: str) -> Optional[Dict]:
        """Holt Summoner-Informationen basierend auf PUUID"""
        url = f"{self.base_url_platform}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_ranked_stats(self, puuid: str) -> Optional[List[Dict]]:
        """Holt Ranked-Statistiken für einen Summoner (direkt via PUUID)"""
        # Neuer PUUID-basierter Endpoint (seit 2024)
        url = f"{self.base_url_platform}/lol/league/v4/entries/by-puuid/{puuid}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return None

    def get_champion_mastery(self, puuid: str, top: int = 10) -> Optional[List[Dict]]:
        """Holt die Champion Mastery Daten"""
        url = f"{self.base_url_platform}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top"
        params = {"count": top}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        return None

    def get_match_history(self, puuid: str, count: int = 5) -> Optional[List[str]]:
        """Holt die Match-IDs der letzten Spiele"""
        url = f"{self.base_url_regional}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"count": count}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        return None

    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Holt detaillierte Informationen zu einem Match"""
        url = f"{self.base_url_regional}/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return None


def generate_stats_json(game_name: str, tag_line: str, api_key: str, output_file: str = "stats.json"):
    """Generiert eine JSON-Datei mit allen Stats für das OBS Overlay"""

    print(f"Generiere Stats für {game_name}#{tag_line}...")

    # Initialisiere APIs
    riot_api = RiotAPI(api_key=api_key)
    ddragon_api = DataDragonAPI()

    # Hole Champion-Daten
    champion_data = ddragon_api.get_champion_data()

    # Hole Account-Info
    account = riot_api.get_account_by_riot_id(game_name, tag_line)
    if not account:
        print("❌ Account nicht gefunden!")
        return False

    puuid = account["puuid"]

    # Hole Summoner-Info
    summoner = riot_api.get_summoner_by_puuid(puuid)
    if not summoner:
        print("❌ Summoner nicht gefunden!")
        return False

    # Hole Ranked Stats
    ranked_stats = riot_api.get_ranked_stats(puuid)
    ranked_data = []
    if ranked_stats:
        for queue in ranked_stats:
            wins = queue.get("wins", 0)
            losses = queue.get("losses", 0)
            winrate = round((wins / (wins + losses) * 100), 1) if (wins + losses) > 0 else 0

            ranked_data.append({
                "queueType": queue.get("queueType"),
                "tier": queue.get("tier", "UNRANKED"),
                "rank": queue.get("rank", ""),
                "leaguePoints": queue.get("leaguePoints", 0),
                "wins": wins,
                "losses": losses,
                "winrate": winrate
            })

    # Hole Champion Mastery
    mastery = riot_api.get_champion_mastery(puuid, top=5)
    champions_data = []
    if mastery:
        for champ in mastery:
            champion_id = champ["championId"]
            champion_name = ddragon_api.get_champion_name_by_id(champion_id, champion_data)
            champion_icon = ddragon_api.get_champion_icon_url(champion_name)

            # Hole den Display-Namen
            display_name = champion_name
            if champion_name in champion_data.get("data", {}):
                display_name = champion_data["data"][champion_name].get("name", champion_name)

            champions_data.append({
                "name": display_name,
                "icon": champion_icon,
                "level": champ["championLevel"],
                "points": champ["championPoints"]
            })

    # Hole Match History
    match_ids = riot_api.get_match_history(puuid, count=5)
    matches_data = []
    last_game_data = None
    if match_ids:
        for match_id in match_ids[:5]:
            match = riot_api.get_match_details(match_id)
            if match:
                info = match["info"]
                # Finde den Spieler im Match
                participant = None
                for p in info["participants"]:
                    if p["puuid"] == puuid:
                        participant = p
                        break

                if participant:
                    champion_name = ddragon_api.get_champion_name_by_id(
                        participant["championId"], champion_data
                    )
                    champion_icon = ddragon_api.get_champion_icon_url(champion_name)

                    # Hole Display-Namen
                    display_name = champion_name
                    if champion_name in champion_data.get("data", {}):
                        display_name = champion_data["data"][champion_name].get("name", champion_name)

                    match_entry = {
                        "champion": display_name,
                        "championIcon": champion_icon,
                        "kills": participant["kills"],
                        "deaths": participant["deaths"],
                        "assists": participant["assists"],
                        "win": participant["win"],
                        "gameDuration": info["gameDuration"] // 60,
                        "gameMode": info.get("gameMode", "CLASSIC")
                    }

                    matches_data.append(match_entry)

                    # Speichere das erste (neueste) Spiel als last_game_data
                    if last_game_data is None:
                        last_game_data = {
                            "champion": display_name,
                            "championIcon": champion_icon,
                            "kills": participant["kills"],
                            "deaths": participant["deaths"],
                            "assists": participant["assists"],
                            "win": participant["win"],
                            "gameDuration": info["gameDuration"] // 60,
                            "gameMode": info.get("gameMode", "CLASSIC"),
                            "totalMinionsKilled": participant.get("totalMinionsKilled", 0),
                            "neutralMinionsKilled": participant.get("neutralMinionsKilled", 0),
                            "goldEarned": participant.get("goldEarned", 0),
                            "totalDamageDealtToChampions": participant.get("totalDamageDealtToChampions", 0),
                            "visionScore": participant.get("visionScore", 0),
                            "champLevel": participant.get("champLevel", 0),
                            "items": [
                                participant.get("item0", 0),
                                participant.get("item1", 0),
                                participant.get("item2", 0),
                                participant.get("item3", 0),
                                participant.get("item4", 0),
                                participant.get("item5", 0),
                                participant.get("item6", 0),
                            ]
                        }

    # Erstelle finale Datenstruktur
    stats_data = {
        "playerName": f"{game_name}#{tag_line}",
        "level": summoner["summonerLevel"],
        "profileIcon": ddragon_api.get_profile_icon_url(summoner["profileIconId"]),
        "ranked": ranked_data,
        "champions": champions_data,
        "matches": matches_data,
        "lastGame": last_game_data,
        "lastUpdate": time.time()
    }

    # Speichere in JSON-Datei
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Stats erfolgreich in '{output_file}' gespeichert!")
    return True


def main():
    # API Key aus Umgebungsvariable oder hier eintragen
    # TRAGE DEINEN API KEY HIER EIN (zwischen den Anführungszeichen):
    API_KEY = os.getenv("RIOT_API_KEY", "RGAPI-575f3234-c4e8-4dc9-91f4-3713a16f3f06")

    if API_KEY == "DEIN-API-KEY-HIER" or API_KEY.startswith("RGAPI-XXXX"):
        print("⚠️  Bitte setze deinen Riot API Key!")
        print("   Bearbeite Zeile 195 in generate_obs_stats.py")
        print("   Oder setze Umgebungsvariable: RIOT_API_KEY")
        return

    # Spieler-Daten
    GAME_NAME = "Piekasso"
    TAG_LINE = "EUW"

    # Generiere Stats einmalig
    print("=== League of Legends OBS Stats Generator ===\n")
    generate_stats_json(GAME_NAME, TAG_LINE, API_KEY)

    print("\n📝 Nächste Schritte:")
    print("   1. Öffne OBS Studio")
    print("   2. Füge eine 'Browser' Quelle hinzu")
    print("   3. Setze die lokale Datei auf: file:///c:/Users/dejaw/Desktop/Claude Code SDK/obs_overlay.html")
    print("   4. Empfohlene Größe: 450x400")
    print("   5. Das Overlay aktualisiert sich automatisch alle 60 Sekunden")
    print("\n💡 Tipp: Führe dieses Script regelmäßig aus, um die Stats zu aktualisieren!")


def run_continuous(interval_seconds: int = 60):
    """Führt das Script kontinuierlich aus (für Live-Updates)"""

    API_KEY = os.getenv("RIOT_API_KEY", "RGAPI-575f3234-c4e8-4dc9-91f4-3713a16f3f06")

    if API_KEY == "DEIN-API-KEY-HIER" or API_KEY.startswith("RGAPI-XXXX"):
        print("⚠️  Bitte setze deinen Riot API Key!")
        print("   Bearbeite Zeile 195 in generate_obs_stats.py")
        return

    GAME_NAME = "Piekasso"
    TAG_LINE = "EUW"

    print("=== Live Stats Generator (Ctrl+C zum Beenden) ===\n")

    while True:
        try:
            success = generate_stats_json(GAME_NAME, TAG_LINE, API_KEY)
            if success:
                print(f"⏰ Nächstes Update in {interval_seconds} Sekunden...\n")
            else:
                print("❌ Fehler beim Generieren der Stats")

            time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n\n👋 Stats Generator beendet!")
            break
        except Exception as e:
            print(f"❌ Fehler: {e}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    import sys

    # Prüfe ob "--live" Parameter übergeben wurde
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        # Live-Modus: Aktualisiere alle 60 Sekunden
        run_continuous(60)
    else:
        # Einmaliger Run
        main()
