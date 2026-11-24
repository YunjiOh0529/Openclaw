import atexit
import json
import os
import sys
import time

LOG_PATH = os.environ.get(
    "SKILL_LOG_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill_log.jsonl"),
)


def start(skill_name):
    rec = {
        "skill": skill_name,
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "start_ts": round(time.time(), 3),
        "run_id": os.environ.get("RUN_ID", ""),
        "args": sys.argv[1:],
    }
    t0 = time.perf_counter()

    def _finish():
        rec["duration_sec"] = round(time.perf_counter() - t0, 3)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    atexit.register(_finish)
    return rec
