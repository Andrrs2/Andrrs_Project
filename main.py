import os
import sys
from datetime import datetime
from pathlib import Path
import zoneinfo
import requests
from dotenv import load_dotenv

# Load local environment variables from .env (used during local testing)
load_dotenv()

from collectors.weather import get_weather_and_aqi
from collectors.sports import get_sports_report
from collectors.transit import get_transit_digest

TIMEZONE = zoneinfo.ZoneInfo("America/Los_Angeles")

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

def generate_report_content():
    now = datetime.now(TIMEZONE)
    date_str = now.strftime("%A, %B %d, %Y")

    # 1. Weather
    try:
        w = get_weather_and_aqi()
        weather_text = (
            f"**Temp:** High {w['temp_high']}°F / Low {w['temp_low']}°F\n"
            f"**Rain Probability:** {w['precip_chance']}%\n"
            f"**Air Quality:** {w['us_aqi']} AQI ({w['aqi_status']})"
        )
    except Exception as e:
        weather_text = f"Unavailable ({e})"

    # 2. Transit
    try:
        transit_updates = get_transit_digest()
        transit_text = "\n".join(transit_updates)
    except Exception as e:
        transit_text = f"Unavailable ({e})"

    # 3. Sports
    try:
        sports = get_sports_report()
        sports_lines = []
        for team, games in sports.items():
            sports_lines.append(f"**{team}**")
            for g in games:
                sports_lines.append(f"• {g}")
        sports_text = "\n".join(sports_lines)
    except Exception as e:
        sports_text = f"Unavailable ({e})"

    return date_str, weather_text, transit_text, sports_text

def send_to_discord(date_str, weather_text, transit_text, sports_text):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ Warning: DISCORD_WEBHOOK_URL not set. Skipping Discord dispatch.")
        return

    payload = {
        "username": "Morning Briefing",
        "avatar_url": "https://img.icons8.com/clouds/200/sun.png",
        "embeds": [
            {
                "title": f"☀️ Morning Digest — {date_str}",
                "color": 3447003,  # Blue accent
                "fields": [
                    {
                        "name": "📍 Weather & Air (90006)",
                        "value": weather_text,
                        "inline": False
                    },
                    {
                        "name": "🚌 LA Metro (20, 30, 33, 204, 207, 720, D Line)",
                        "value": transit_text,
                        "inline": False
                    },
                    {
                        "name": "⚾🏀 Dodgers & Lakers",
                        "value": sports_text,
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Automated Daily Runner"
                },
                "timestamp": datetime.now(zoneinfo.ZoneInfo("UTC")).isoformat()
            }
        ]
    }

    res = requests.post(webhook_url, json=payload, timeout=10)
    res.raise_for_status()
    print("✅ Report successfully posted to Discord!")

def run_digest():
    date_str, weather_text, transit_text, sports_text = generate_report_content()

    # Print to console
    print(f"=== {date_str} ===")
    print(weather_text)
    print("\n--- Transit ---")
    print(transit_text)
    print("\n--- Sports ---")
    print(sports_text)

    # Deliver to Discord
    send_to_discord(date_str, weather_text, transit_text, sports_text)

if __name__ == "__main__":
    run_digest()