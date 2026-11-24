import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import local_config
import skill_logger

LOG = skill_logger.start("memory-pattern")
DATA = os.environ.get("MEMORY_DATA_PATH",
                      os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory_data.json"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="")
    ap.add_argument("--top", type=int, default=3)
    a = ap.parse_args()
    LOG["category"] = a.category
    try:
        with open(DATA, encoding="utf-8") as f:
            visits = json.load(f).get("visits", [])
        stats = defaultdict(lambda: {"visits": 0, "last_visit": "", "category": ""})
        for v in visits:
            if a.category and a.category not in v.get("category", ""):
                continue
            s = stats[v["place"]]
            s["visits"] += 1
            s["category"] = v.get("category", "")
            s["last_visit"] = max(s["last_visit"], v.get("visited_at", ""))
        ranked = sorted(stats.items(), key=lambda kv: (-kv[1]["visits"], kv[0]))
        results = [{"place": p, **s} for p, s in ranked[: max(1, a.top)]]
        out = {"status": "ok" if results else "empty", "category": a.category, "results": results}
    except (OSError, ValueError, KeyError) as e:
        out = {"status": "error", "error": str(e), "results": []}
    LOG["api_status"], LOG["n_results"] = out["status"], len(out["results"])
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
