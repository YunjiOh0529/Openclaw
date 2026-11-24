import json
import os
import shutil
import sys

CFG = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "config.local.json")
BAK = CFG + ".before_apifail_test"
KEYS = ["GOOGLE_PLACES_API_KEY", "NAVER_CLIENT_ID", "NAVER_CLIENT_SECRET"]


def status():
    d = json.load(open(CFG, encoding="utf-8"))
    broken = all(str(d.get(k, "")).startswith("INVALID") for k in KEYS)
    print("keys are BROKEN (test mode)" if broken else "keys are NORMAL")
    print("backup exists:", os.path.exists(BAK))


cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
if cmd == "break":
    if os.path.exists(BAK):
        sys.exit("A backup already exists. Run 'py api_keys.py restore' first.")
    shutil.copy(CFG, BAK)
    d = json.load(open(CFG, encoding="utf-8"))
    for k in KEYS:
        d[k] = "INVALID_FOR_API_FAILURE_TEST"
    json.dump(d, open(CFG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("backup saved, keys broken")
elif cmd == "restore":
    if not os.path.exists(BAK):
        sys.exit("No backup found. Nothing changed.")
    shutil.copy(BAK, CFG)
    os.remove(BAK)
    print("original config restored")
status()
