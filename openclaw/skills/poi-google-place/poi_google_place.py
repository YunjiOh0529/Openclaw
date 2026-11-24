import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import local_config
import skill_logger

LOG = skill_logger.start("poi-google-place")


CENTER_LAT = float(os.environ.get("POI_CENTER_LAT", "37.5913"))
CENTER_LNG = float(os.environ.get("POI_CENTER_LNG", "127.0221"))
RADIUS_M = float(os.environ.get("POI_RADIUS_M", "1000"))
MAX_RESULTS = 5
URL = "https://places.googleapis.com/v1/places:searchText"


def distance_m(lat1, lng1, lat2, lng2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def search(keyword, area=""):
    query = f"{area} {keyword}".strip()
    LOG["query"] = query
    body = {
        "textQuery": query,
        "languageCode": "ko",
        "regionCode": "KR",
        "maxResultCount": 20,
        "locationBias": {
            "circle": {
                "center": {"latitude": CENTER_LAT, "longitude": CENTER_LNG},
                "radius": RADIUS_M,
            }
        },
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": os.environ["GOOGLE_PLACES_API_KEY"],
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.location",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
    for p in data.get("places", []):
        loc = p.get("location", {})
        if "latitude" not in loc:
            continue
        d = distance_m(CENTER_LAT, CENTER_LNG, loc["latitude"], loc["longitude"])
        if d <= RADIUS_M:
            results.append({
                "name": p.get("displayName", {}).get("text", ""),
                "address": p.get("formattedAddress", ""),
                "rating": p.get("rating"),
                "distance_m": round(d),
            })
    results.sort(key=lambda x: x["distance_m"])
    return results[:MAX_RESULTS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyword", required=True)
    ap.add_argument("--area", default="")
    a = ap.parse_args()
    try:
        results = search(a.keyword, a.area)
        status = "ok" if results else "empty"
        out = {"status": status, "query": LOG.get("query"), "radius_m": RADIUS_M, "results": results}
    except (urllib.error.URLError, KeyError, ValueError) as e:
        status = "error"
        out = {"status": status, "error": str(e), "results": []}
    LOG["api_status"] = status
    LOG["n_results"] = len(out["results"])
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
