# -*- coding: utf-8 -*-
import requests
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "RGAPI-50c19471-ea4c-409d-9637-2741fc955b4b"
PUUID = "1uoyWWdbG6RTNK745zuCpw78-3BDy0oRGWXsWlNBWRN9K19iqsAKpeymz4WAIGphImWP53jQ5yIg5A"

headers = {"X-Riot-Token": API_KEY}

print("🔄 Force Update: Hole Ranked Stats direkt...")

# Hole Ranked Stats mit neuem Endpoint
url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{PUUID}"
response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    ranked_data_raw = response.json()
    print(f"✅ Ranked Stats gefunden: {len(ranked_data_raw)} Queues")

    # Lade aktuelle stats.json
    with open("stats.json", "r", encoding="utf-8") as f:
        stats = json.load(f)

    # Update ranked stats
    ranked_data = []
    for queue in ranked_data_raw:
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

    stats["ranked"] = ranked_data

    # Speichere
    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print("✅ stats.json aktualisiert!")
    print(json.dumps(ranked_data, indent=2))
else:
    print(f"❌ Fehler: {response.text}")
