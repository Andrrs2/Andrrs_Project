import requests

DEFAULT_LAT = 34.0481
DEFAULT_LON = -118.2941

def get_weather_and_aqi(latitude: float = DEFAULT_LAT, longitude: float = DEFAULT_LON) -> dict:
    # 1. Weather forecast
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "timezone": "America/Los_Angeles",
        "forecast_days": 1,
    }
    w_res = requests.get(weather_url, params=weather_params, timeout=10)
    w_res.raise_for_status()
    w_data = w_res.json()["daily"]

    # 2. Air Quality Index
    aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    aqi_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["us_aqi", "pm2_5"],
        "timezone": "America/Los_Angeles",
    }
    a_res = requests.get(aqi_url, params=aqi_params, timeout=10)
    a_res.raise_for_status()
    a_data = a_res.json()["current"]

    aqi_val = a_data.get("us_aqi")
    aqi_status = "Unknown"
    if aqi_val is not None:
        if aqi_val <= 50:
            aqi_status = "Good"
        elif aqi_val <= 100:
            aqi_status = "Moderate"
        elif aqi_val <= 150:
            aqi_status = "Unhealthy for Sensitive Groups"
        elif aqi_val <= 200:
            aqi_status = "Unhealthy"
        else:
            aqi_status = "Very Unhealthy"

    return {
        "temp_high": round(w_data["temperature_2m_max"][0]),
        "temp_low": round(w_data["temperature_2m_min"][0]),
        "precip_chance": w_data["precipitation_probability_max"][0],
        "us_aqi": aqi_val,
        "aqi_status": aqi_status,
        "pm2_5": a_data.get("pm2_5"),
    }

if __name__ == "__main__":
    data = get_weather_and_aqi()
    print("Test output:", data)