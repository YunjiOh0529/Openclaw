import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import local_config
import skill_logger

LOG = skill_logger.start("lastfm-music")
API = "https://ws.audioscrobbler.com/2.0/"
DATA = os.environ.get("MEMORY_DATA_PATH",
                      os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory_data.json"))


def call(method, **params):
    q = urllib.parse.urlencode({"method": method, "api_key": os.environ["LASTFM_API_KEY"],
                                "format": "json", "autocorrect": 1, **params})
    with urllib.request.urlopen(f"{API}?{q}", timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "error" in data:
        raise ValueError(data.get("message", "Last.fm error"))
    return data


def artist_tracks(artist, limit=5):
    tracks = call("artist.gettoptracks", artist=artist, limit=limit).get("toptracks", {}).get("track", [])
    return [{"title": t["name"], "artist": t["artist"]["name"]} for t in tracks]


def taste_tracks(limit=5):
    with open(DATA, encoding="utf-8") as f:
        prefs = json.load(f).get("preferences", {})
    results = []
    for tag in prefs.get("music_genres", [])[:2]:
        tracks = call("tag.gettoptracks", tag=tag, limit=3).get("tracks", {}).get("track", [])
        results += [{"title": t["name"], "artist": t["artist"]["name"], "reason": f"genre: {tag}"} for t in tracks]
    for fav in prefs.get("favorite_artists", [])[:1]:
        sims = call("artist.getsimilar", artist=fav, limit=2).get("similarartists", {}).get("artist", [])
        for s in sims:
            top = artist_tracks(s["name"], limit=1)
            results += [{**t, "reason": f"similar to {fav}"} for t in top]
    return results[: limit + 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="artist", choices=["artist", "taste"])
    ap.add_argument("--artist", default="")
    a = ap.parse_args()
    LOG["mode"], LOG["artist"] = a.mode, a.artist
    try:
        if a.mode == "artist":
            if not a.artist:
                raise ValueError("artist is required for mode=artist")
            results = artist_tracks(a.artist)
        else:
            results = taste_tracks()
        out = {"status": "ok" if results else "empty", "mode": a.mode, "results": results}
    except (urllib.error.URLError, KeyError, ValueError, OSError) as e:
        out = {"status": "error", "error": str(e), "results": []}
    LOG["api_status"], LOG["n_results"] = out["status"], len(out["results"])
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
