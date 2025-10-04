# -*- coding: utf-8 -*-
import requests
import os
from typing import Dict, List, Optional


class RiotAPI:
    """Client für die Riot Games API um League of Legends Daten abzurufen"""

    def __init__(self, api_key: str, region: str = "europe"):
        self.api_key = api_key
        self.region = region  # europe, americas, asia
        self.platform = "euw1"  # euw1 für EUW
        self.base_url_regional = f"https://{self.region}.api.riotgames.com"
        self.base_url_platform = f"https://{self.platform}.api.riotgames.com"
        self.headers = {"X-Riot-Token": self.api_key}

    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Optional[Dict]:
        """Holt Account-Informationen basierend auf Riot ID (z.B. Piekasso#EUW)"""
        url = f"{self.base_url_regional}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fehler beim Abrufen des Accounts: {response.status_code}")
            print(response.text)
            return None

    def get_summoner_by_puuid(self, puuid: str) -> Optional[Dict]:
        """Holt Summoner-Informationen basierend auf PUUID"""
        url = f"{self.base_url_platform}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fehler beim Abrufen des Summoners: {response.status_code}")
            return None

    def get_ranked_stats(self, puuid: str) -> Optional[List[Dict]]:
        """Holt Ranked-Statistiken für einen Summoner (via PUUID)"""
        # Riot API benötigt die encrypted summoner ID für ranked stats
        # Diese müssen wir über einen separaten Endpunkt holen
        summoner_url = f"{self.base_url_platform}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        summoner_response = requests.get(summoner_url, headers=self.headers)

        if summoner_response.status_code != 200:
            print(
                f"Fehler beim Abrufen des Summoners für Ranked Stats: {summoner_response.status_code}")
            return None

        summoner_data = summoner_response.json()
        encrypted_id = summoner_data.get("id")

        if not encrypted_id:
            print("Keine verschlüsselte Summoner ID gefunden")
            return None

        url = f"{self.base_url_platform}/lol/league/v4/entries/by-summoner/{encrypted_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Fehler beim Abrufen der Ranked Stats: {response.status_code}")
            print(response.text)
            return None

    def get_match_history(self, puuid: str, count: int = 20) -> Optional[List[str]]:
        """Holt die Match-IDs der letzten Spiele"""
        url = f"{self.base_url_regional}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"count": count}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Fehler beim Abrufen der Match History: {response.status_code}")
            return None

    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Holt detaillierte Informationen zu einem Match"""
        url = f"{self.base_url_regional}/lol/match/v5/matches/{match_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Fehler beim Abrufen der Match Details: {response.status_code}")
            return None

    def get_champion_mastery(self, puuid: str, top: int = 10) -> Optional[List[Dict]]:
        """Holt die Champion Mastery Daten"""
        url = f"{self.base_url_platform}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top"
        params = {"count": top}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Fehler beim Abrufen der Champion Mastery: {response.status_code}")
            return None


def main():
    # API Key aus Umgebungsvariable laden oder hier eintragen
    API_KEY = os.getenv(
        "RIOT_API_KEY", "RGAPI-50c19471-ea4c-409d-9637-2741fc955b4b")

    if API_KEY == "DEIN-API-KEY-HIER":
        print("Bitte setze deinen Riot API Key!")
        print("Hol dir einen Key von: https://developer.riotgames.com/")
        print("Dann setze die Umgebungsvariable RIOT_API_KEY oder trage ihn direkt im Code ein.")
        return

    # Riot API Client initialisieren
    client = RiotAPI(api_key=API_KEY)

    # Spieler: Piekasso#EUW
    game_name = "Piekasso"
    tag_line = "EUW"

    print(f"Suche nach Spieler: {game_name}#{tag_line}\n")

    # 1. Account-Informationen abrufen
    account = client.get_account_by_riot_id(game_name, tag_line)
    if not account:
        print("Spieler nicht gefunden!")
        return

    puuid = account["puuid"]
    print(f"Account gefunden!")
    print(f"PUUID: {puuid}\n")

    # 2. Summoner-Informationen abrufen
    summoner = client.get_summoner_by_puuid(puuid)
    if summoner:
        print(f"Summoner Level: {summoner['summonerLevel']}\n")
    else:
        print("Summoner-Informationen konnten nicht abgerufen werden!")
        return

    # 3. Ranked Stats abrufen (verwendet PUUID)
    ranked_stats = client.get_ranked_stats(puuid)
    if ranked_stats:
        print("Ranked Statistiken:")
        for queue in ranked_stats:
            queue_type = queue.get("queueType", "Unknown")
            tier = queue.get("tier", "UNRANKED")
            rank = queue.get("rank", "")
            lp = queue.get("leaguePoints", 0)
            wins = queue.get("wins", 0)
            losses = queue.get("losses", 0)
            winrate = (wins / (wins + losses) *
                       100) if (wins + losses) > 0 else 0

            print(f"   {queue_type}: {tier} {rank} - {lp} LP")
            print(f"   W/L: {wins}/{losses} ({winrate:.1f}% Winrate)\n")

    # 4. Match History abrufen
    print("Lade Match History...")
    match_ids = client.get_match_history(puuid, count=5)
    if match_ids:
        print(f"Letzte {len(match_ids)} Spiele:\n")

        for i, match_id in enumerate(match_ids[:5], 1):
            match = client.get_match_details(match_id)
            if match:
                info = match["info"]
                # Finde den Spieler im Match
                participant = None
                for p in info["participants"]:
                    if p["puuid"] == puuid:
                        participant = p
                        break

                if participant:
                    champion = participant["championName"]
                    kills = participant["kills"]
                    deaths = participant["deaths"]
                    assists = participant["assists"]
                    win = "Sieg" if participant["win"] else "Niederlage"
                    game_duration = info["gameDuration"] // 60

                    print(
                        f"   {i}. {champion} - {kills}/{deaths}/{assists} - {win} ({game_duration}min)")

    # 5. Champion Mastery abrufen
    print("\nTop Champions (Mastery):")
    mastery = client.get_champion_mastery(puuid, top=5)
    if mastery:
        for i, champ in enumerate(mastery, 1):
            champion_id = champ["championId"]
            level = champ["championLevel"]
            points = champ["championPoints"]
            print(
                f"   {i}. Champion ID {champion_id}: Level {level} - {points:,} Punkte")


if __name__ == "__main__":
    main()
