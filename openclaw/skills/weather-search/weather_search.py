import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import local_config
import skill_logger

LOG = skill_logger.start("weather-search")
API = "https://api.openweathermap.org"
DEFAULT_LAT = float(os.environ.get("WEATHER_LAT", os.environ.get("POI_CENTER_LAT", "37.5913")))
DEFAULT_LNG = float(os.environ.get("WEATHER_LNG", os.environ.get("POI_CENTER_LNG", "127.0221")))
DEFAULT_NAMES = {"", "서울", "seoul", "현재 위치", "여기", "성신여대", "성북구"}


def get_json(path, **params):
    params["appid"] = os.environ["OPENWEATHER_API_KEY"].strip()
    with urllib.request.urlopen(f"{API}{path}?{urllib.parse.urlencode(params)}", timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def resolve(location):
    if location.strip().lower() in DEFAULT_NAMES:
        return DEFAULT_LAT, DEFAULT_LNG, "서울 (현재 위치)"
    res = get_json("/geo/1.0/direct", q=location, limit=1)
    if not res:
        raise ValueError(f"location not found: {location}")
    g = res[0]
    name = (g.get("local_names") or {}).get("ko") or g.get("name", location)
    return g["lat"], g["lon"], f"{name}, {g.get('country', '')}".strip(", ")


def get_weather(location):
    lat, lon, name = resolve(location)
    cur = get_json("/data/2.5/weather", lat=lat, lon=lon, units="metric", lang="kr")
    fc = get_json("/data/2.5/forecast", lat=lat, lon=lon, units="metric", lang="kr")

    tz = datetime.timezone(datetime.timedelta(seconds=fc.get("city", {}).get("timezone", 32400)))
    now = datetime.datetime.now(tz)
    entries = [(datetime.datetime.fromtimestamp(e["dt"], tz), e) for e in fc.get("list", [])]
    today = [e for t, e in entries if t.date() == now.date()]
    window = today or [e for _, e in entries[:3]]

    temps = [cur["main"]["temp"]] + [e["main"]["temp"] for e in window]
    pops = [round(e.get("pop", 0) * 100) for e in window]
    rain_desc = sorted({e["weather"][0]["description"] for e in window
                        if e["weather"][0]["main"] in ("Rain", "Drizzle", "Thunderstorm", "Snow")})
    return {
        "location": name, "local_time": now.strftime("%Y-%m-%d %H:%M"),
        "condition": cur["weather"][0]["description"],
        "temperature_c": cur["main"]["temp"], "feels_like_c": cur["main"].get("feels_like"),
        "humidity_pct": cur["main"]["humidity"],
        "precipitation_1h_mm": (cur.get("rain") or {}).get("1h", 0) + (cur.get("snow") or {}).get("1h", 0),
        "today": {"max_c": max(temps), "min_c": min(temps),
                  "rain_probability_max_pct": max(pops) if pops else None,
                  "rain_expected": rain_desc or "없음",
                  "period": "rest of today" if today else "next 9 hours"},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--location", default="")
    a = ap.parse_args()
    LOG["location"] = a.location
    try:
        w = get_weather(a.location)
        out = {"status": "ok", "weather": w, "results": [w]}
    except (urllib.error.URLError, KeyError, ValueError, TypeError, IndexError) as e:
        out = {"status": "error", "error": str(e), "results": []}
    LOG["api_status"], LOG["n_results"] = out["status"], len(out["results"])
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
