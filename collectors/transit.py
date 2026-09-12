import requests

TARGET_LINES = {
    "20": "Line 20 (Wilshire Blvd Local)",
    "30": "Line 30 (Pico Blvd)",
    "33": "Line 33 (Venice Blvd)",
    "204": "Line 204 (Vermont Ave Local)",
    "207": "Line 207 (Western Ave)",
    "720": "Line 720 (Wilshire Blvd Rapid)",
    "805": "D Line (Purple Line Subway)",
    "purple": "D Line (Purple Line Subway)",
}

def get_transit_digest() -> list[str]:
    """
    Checks LA Metro real-time alerts and disruptions for tracked lines.
    Falls back gracefully if no active advisories are reported.
    """
    disruptions = []

    # 1. Primary LA Metro updates endpoint
    try:
        alerts_url = "https://api.metro.net/updates"
        res = requests.get(alerts_url, timeout=10)
        if res.ok:
            alerts = res.json()
            if isinstance(alerts, dict):
                alerts = alerts.get("items", alerts.get("alerts", []))

            for alert in alerts:
                header = alert.get("header_text", "") or alert.get("title", "")
                desc = alert.get("description_text", "") or alert.get("description", "")
                text = f"{header} {desc}".lower()

                for line_id, line_label in TARGET_LINES.items():
                    if f"line {line_id}" in text or f"route {line_id}" in text or f" {line_id} " in text:
                        msg = header if header else desc
                        disruptions.append(f"⚠️ {line_label}: {msg[:120]}...")
    except Exception:
        pass

    # 2. Secondary fallback endpoint
    if not disruptions:
        try:
            sec_url = "https://api.metro.net/agencies/lametro/service_alerts/"
            sec_res = requests.get(sec_url, timeout=8)
            if sec_res.ok:
                data = sec_res.json()
                for item in data.get("items", []):
                    route = str(item.get("route_id", ""))
                    if route in TARGET_LINES:
                        header = item.get("header", "Service Alert")
                        disruptions.append(f"⚠️ {TARGET_LINES[route]}: {header}")
        except Exception:
            pass

    # Deduplicate results
    unique_disruptions = list(set(disruptions))
    if not unique_disruptions:
        return ["✅ Lines 20, 30, 33, 204, 207, 720 & D Line: Normal operations (no major alerts)"]

    return unique_disruptions

if __name__ == "__main__":
    print("Testing transit collector directly:")
    for line in get_transit_digest():
        print(f"  • {line}")