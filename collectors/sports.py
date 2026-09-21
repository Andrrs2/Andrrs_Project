from datetime import datetime, timedelta
import zoneinfo
import requests

def get_team_summary(sport: str, league: str, team_name: str) -> str:
    """
    Fetches yesterday's result and today's schedule for a team using single-date queries.
    """
    tz = zoneinfo.ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz)
    yesterday_str = (now - timedelta(days=1)).strftime("%Y%m%d")
    today_str = now.strftime("%Y%m%d")

    base_url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    headers = {"User-Agent": "Mozilla/5.0"}

    recent_game_text = None
    upcoming_game_text = None

    # 1. Check Yesterday's Score
    try:
        res_yest = requests.get(f"{base_url}?dates={yesterday_str}", headers=headers, timeout=10)
        if res_yest.ok:
            data = res_yest.json()
            for event in data.get("events", []):
                if team_name.lower() in event.get("name", "").lower():
                    # Parse final score
                    comp = event["competitions"][0]
                    t1 = comp["competitors"][0]
                    t2 = comp["competitors"][1]
                    status = comp.get("status", {}).get("type", {}).get("description", "Final")
                    recent_game_text = f"Yesterday: {t1['team']['shortDisplayName']} {t1.get('score', '')} - {t2['team']['shortDisplayName']} {t2.get('score', '')} ({status})"
                    break
    except Exception:
        pass

    # 2. Check Today's Game / Status
    try:
        res_today = requests.get(f"{base_url}?dates={today_str}", headers=headers, timeout=10)
        if res_today.ok:
            data = res_today.json()
            for event in data.get("events", []):
                if team_name.lower() in event.get("name", "").lower():
                    comp = event["competitions"][0]
                    status_desc = comp.get("status", {}).get("type", {}).get("description", "Scheduled")
                    
                    if "Final" in status_desc:
                        t1 = comp["competitors"][0]
                        t2 = comp["competitors"][1]
                        upcoming_game_text = f"Today: {t1['team']['shortDisplayName']} {t1.get('score', '')} - {t2['team']['shortDisplayName']} {t2.get('score', '')} (Final)"
                    else:
                        start_time = comp.get("status", {}).get("type", {}).get("shortDetail", "Today")
                        upcoming_game_text = f"Today: vs {event.get('shortName', team_name)} ({start_time})"
                    break
    except Exception:
        pass

    # Combine status
    if upcoming_game_text:
        return f"{recent_game_text} | {upcoming_game_text}" if recent_game_text else upcoming_game_text
    if recent_game_text:
        return f"{recent_game_text} | No game scheduled today"
    
    return "Off-season / No games scheduled"

def get_sports_report() -> dict:
    return {
        "Dodgers": [get_team_summary("baseball", "mlb", "Dodgers")],
        "Lakers": [get_team_summary("basketball", "nba", "Lakers")],
    }

if __name__ == "__main__":
    print(get_sports_report())