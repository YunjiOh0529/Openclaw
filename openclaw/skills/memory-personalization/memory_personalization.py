import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import local_config
import skill_logger

LOG = skill_logger.start("memory-personalization")
DATA = os.environ.get("MEMORY_DATA_PATH",
                      os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory_data.json"))
READONLY = os.environ.get("MEMORY_READONLY", "1") == "1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", default="get", choices=["get", "set"])
    ap.add_argument("--key", default="")
    ap.add_argument("--value", default="")
    a = ap.parse_args()
    LOG["action"], LOG["key"] = a.action, a.key
    try:
        with open(DATA, encoding="utf-8") as f:
            data = json.load(f)
        prefs = data.get("preferences", {})
        if a.action == "get":
            if a.key:
                found = a.key in prefs
                out = {"status": "ok" if found else "empty", "results": [{a.key: prefs[a.key]}] if found else []}
            else:
                out = {"status": "ok" if prefs else "empty", "results": [prefs] if prefs else []}
        elif READONLY:
            out = {"status": "readonly", "note": "memory is read-only during experiments", "results": []}
        else:
            prefs[a.key] = a.value
            data["preferences"] = prefs
            with open(DATA, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            out = {"status": "ok", "results": [{a.key: a.value}]}
    except (OSError, ValueError) as e:
        out = {"status": "error", "error": str(e), "results": []}
    LOG["api_status"], LOG["n_results"] = out["status"], len(out["results"])
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
