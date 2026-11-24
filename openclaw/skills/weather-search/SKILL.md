---
name: weather-search
description: Retrieve real-time weather for a location (default: the vehicle's current location in Seoul; other cities and countries are also supported) from the OpenWeather API, including current condition, temperature, humidity, precipitation, and today's rain probability and high/low temperatures. Use this when the driver asks about the weather or anything that depends on it.
---

# weather-search

Uses the OpenWeather Current Weather API and the 5-day / 3-hour Forecast API.
Other locations are resolved with the OpenWeather Geocoding API.

## How to run

Run from the workspace root (use `python3` instead of `python` if needed).

```bash
python skills/weather-search/weather_search.py --location "<city name, optional; default = current location (Seoul)>"
```

## Output

JSON with `status` and `weather` (condition, temperature_c, humidity_pct, precipitation_1h_mm,
today: max/min temperature, rain probability, rain expected).
Tell the driver the weather in Korean.
