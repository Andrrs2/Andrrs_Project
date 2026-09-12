from datetime import datetime, timedelta
import zoneinfo
import requests

TIMEZONE = zoneinfo.ZoneInfo("America/Los_Angeles")

TRACKED_TEAMS = [
    {
        "name": "Dodgers",
        "sport": "baseball",
        "league": "mlb",
    },
    {
        "name": "Lakers",
        "sport": "basketball",
        "league": "nba",
    },
]

def format_game(event: dict) -> str:
    """Formats an ESPN event into a clean line item."""
    competition = event["competitions"][0]
    status_type = competition["status"]["type"]["name"]  # STATUS_FINAL, STATUS_SCHEDULED, STATUS_IN_PROGRESS
    status_detail = competition["status"]["type"]["detail"]
    competitors = competition["competitors"]

    # ESPN typically puts home team at index 0, away at index 1
    home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
    away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

    home_name = home["team"]["shortDisplayName"]
    away_name = away["team"]["shortDisplayName"]

    if status_type == "STATUS_FINAL":
        home_score = home.get("score", "0")
        away_score = away.get("score", "0")
        return f"FINAL: {away_name} {away_score} @ {home_name} {home_score}"

    elif status_type == "STATUS_IN_PROGRESS":
        home_score = home.get("score", "0")
        away_score = away.get("score", "0")
        return f"LIVE: {away_name} {away_score} @ {home_name} {home_score} ({status_detail})"

    else:
        # Scheduled game - parse start time into local Pacific time
        start_utc = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        start_local = start_utc.astimezone(TIMEZONE).strftime("%I:%M %p PT")
        return f"TODAY: {away_name} @ {home_name} ({start_local})"

def get_team_digest(sport: str, league: str, team_keyword: str) -> list[str]:
    """Fetches yesterday and today's games for a specific team."""
    now = datetime.now(TIMEZONE)
    yesterday = (now - timedelta(days=1)).strftime("%Y%m%d")
    today = now.strftime("%Y%m%d")
    date_range = f"{yesterday}-{today}"

    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    params = {"dates": date_range, "limit": 100}

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        events = res.json().get("events", [])
    except Exception as e:
        return [f"Error checking {team_keyword}: {e}"]

    team_updates = []
    for event in events:
        name = event.get("name", "")
        if team_keyword.lower() in name.lower():
            team_updates.append(format_game(event))

    if not team_updates:
        return [f"No game yesterday or today (Off Day / Offseason)"]

    return team_updates

def get_sports_report() -> dict[str, list[str]]:
    """Returns aggregated reports for both Lakers and Dodgers."""
    report = {}
    for team in TRACKED_TEAMS:
        report[team["name"]] = get_team_digest(
            sport=team["sport"],
            league=team["league"],
            team_keyword=team["name"]
        )
    return report

if __name__ == "__main__":
    print("Testing Sports Collector...\n")
    results = get_sports_report()
    for team, updates in results.items():
        print(f"**{team}**")
        for line in updates:
            print(f"  • {line}")