import os
import sys
from datetime import datetime
import zoneinfo

# Collector imports
from collectors.weather import get_weather_and_aqi
from collectors.sports import get_sports_report
from collectors.transit import get_transit_digest

TIMEZONE = zoneinfo.ZoneInfo("America/Los_Angeles")

def generate_report() -> str:
    now = datetime.now(TIMEZONE)
    date_str = now.strftime("%A, %B %d, %Y")
    
    sections = []
    
    # Header
    sections.append(f"☀️ MORNING DIGEST — {date_str}")
    sections.append("=" * 35)

    # 1. Weather & AQI (90006 / Central LA)
    try:
        w = get_weather_and_aqi()
        weather_section = (
            "📍 Pico-Union / Koreatown (90006)\n"
            f"🌡️ High: {w['temp_high']}°F  |  Low: {w['temp_low']}°F\n"
            f"🌧️ Rain Chance: {w['precip_chance']}%\n"
            f"🍃 Air Quality: {w['us_aqi']} AQI ({w['aqi_status']})"
        )
    except Exception as e:
        weather_section = f"📍 Weather (90006): Error retrieving forecast ({e})"
    sections.append(weather_section)

    # 2. Transit (Lines 20, 30, 33, 204, 207, 720, D Line)
    sections.append("\n🚌 LA METRO TRANSIT")
    sections.append("-" * 35)
    try:
        transit_updates = get_transit_digest()
        sections.append("\n".join(f"• {line}" for line in transit_updates))
    except Exception as e:
        sections.append(f"• Error retrieving transit alerts ({e})")

    # 3. Sports (Dodgers & Lakers)
    sections.append("\n⚾🏀 SPORTS UPDATE")
    sections.append("-" * 35)
    try:
        sports_data = get_sports_report()
        sports_lines = []
        for team, updates in sports_data.items():
            sports_lines.append(f"• {team}:")
            for line in updates:
                sports_lines.append(f"    - {line}")
        sections.append("\n".join(sports_lines))
    except Exception as e:
        sections.append(f"• Error retrieving sports scores ({e})")

    # Final text assembly
    report_text = "\n".join(sections)
    return report_text

def run_digest():
    report = generate_report()
    print(report)
    
    # Optional: Save to local text file as today's archive
    # with open("latest_report.txt", "w", encoding="utf-8") as f:
    #     f.write(report)
        
    return report

if __name__ == "__main__":
    run_digest()