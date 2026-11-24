import argparse
import csv
import datetime
import json
import os
import random
import subprocess
import sys
import time
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills"))
import local_config

from google import genai
from google.genai import types
from google.genai import errors as genai_errors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")
COMMANDS_CSV = os.path.join(ROOT, "commands", "level5_commands.csv")
DEFAULT_OUT = os.path.join(ROOT, "results", "baseline_results.csv")

def normalize_model(name):

    name = (name or "").strip().strip('"').strip("'").strip()
    for prefix in ("google/", "models/"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name


MODEL = normalize_model(os.environ.get("GEMINI_MODEL", "gemini-3.1-pro"))
SYSTEM_PROMPT = (
    "You are an in-vehicle AI assistant. Answer the driver in Korean. "
    "Use the available tools when they are needed to answer."
)
API_VERSION = os.environ.get("GEMINI_API_VERSION", "v1beta")


def make_client():
    return genai.Client(http_options=types.HttpOptions(api_version=API_VERSION))


MAX_STEPS = 5
TOOL_TIMEOUT_SEC = 60


def skill_description(skill_name):

    path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("description:"):
                return line.split(":", 1)[1].strip()
    raise ValueError(f"No description in {path}")


S = types.Schema
T = types.Type


def _skill(folder, script):
    return os.path.join(SKILLS_DIR, folder, script)


TOOLS = {
    "poi-google-place": {
        "script": _skill("poi-google-place", "poi_google_place.py"),
        "params": S(type=T.OBJECT, properties={
            "keyword": S(type=T.STRING, description="Type of place to find, e.g., 약국, 카페, 주유소."),
            "area": S(type=T.STRING, description="Landmark or area name, e.g., 성신여대. Empty = current location."),
        }, required=["keyword"]),
        "to_argv": lambda a: ["--keyword", str(a.get("keyword", "")), "--area", str(a.get("area", ""))],
    },
    "naver-local-search": {
        "script": _skill("naver-local-search", "naver_news.py"),
        "params": S(type=T.OBJECT, properties={
            "query": S(type=T.STRING, description="News topic or keyword, e.g., 스포츠, 경제, IT."),
            "date": S(type=T.STRING, description="Publication date in YYYY-MM-DD. Empty = latest news."),
        }, required=["query"]),
        "to_argv": lambda a: ["--query", str(a.get("query", "")), "--date", str(a.get("date", ""))],
    },
    "weather-search": {
        "script": _skill("weather-search", "weather_search.py"),
        "params": S(type=T.OBJECT, properties={
            "location": S(type=T.STRING, description="City name (any country). Empty = current location (Seoul)."),
        }),
        "to_argv": lambda a: ["--location", str(a.get("location", ""))],
    },
    "memory-pattern": {
        "script": _skill("memory-pattern", "memory_pattern.py"),
        "params": S(type=T.OBJECT, properties={
            "category": S(type=T.STRING, description="Place category filter, e.g., 카페. Empty = all."),
            "top": S(type=T.INTEGER, description="Number of places to return (default 3)."),
        }),
        "to_argv": lambda a: ["--category", str(a.get("category", "")), "--top", str(int(a.get("top", 3) or 3))],
    },
    "memory-personalization": {
        "script": _skill("memory-personalization", "memory_personalization.py"),
        "params": S(type=T.OBJECT, properties={
            "action": S(type=T.STRING, description="get or set."),
            "key": S(type=T.STRING, description="favorite_cafe, favorite_artists, or music_genres. Empty = all."),
            "value": S(type=T.STRING, description="Value to remember (only for set)."),
        }),
        "to_argv": lambda a: ["--action", str(a.get("action", "get") or "get"), "--key", str(a.get("key", "")),
                              "--value", str(a.get("value", ""))],
    },
    "lastfm-music": {
        "script": _skill("lastfm-music", "lastfm_music.py"),
        "params": S(type=T.OBJECT, properties={
            "mode": S(type=T.STRING, description="artist (songs by an artist) or taste (based on the driver's taste)."),
            "artist": S(type=T.STRING, description="Artist name (only for mode=artist)."),
        }),
        "to_argv": lambda a: ["--mode", str(a.get("mode", "artist") or "artist"), "--artist", str(a.get("artist", ""))],
    },
}


def system_prompt():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    return SYSTEM_PROMPT + f" Current date and time: {now:%Y-%m-%d (%A) %H:%M} (Korea Standard Time)."


def build_config():
    decls = [
        types.FunctionDeclaration(name=name, description=skill_description(name), parameters=t["params"])
        for name, t in TOOLS.items()
    ]
    return types.GenerateContentConfig(
        system_instruction=system_prompt(),
        tools=[types.Tool(function_declarations=decls)],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )


def run_tool(name, args, run_id):
    t = TOOLS[name]
    env = os.environ.copy()
    env["RUN_ID"] = run_id
    env["PYTHONIOENCODING"] = "utf-8"
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, t["script"]] + t["to_argv"](args),
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=TOOL_TIMEOUT_SEC,
    )
    elapsed = time.perf_counter() - t0
    out = proc.stdout.strip() or json.dumps({"status": "error", "error": proc.stderr.strip()[-500:]})
    try:
        parsed = json.loads(out)
        status, n = parsed.get("status", ""), len(parsed.get("results", []))
    except json.JSONDecodeError:
        status, n = "error", 0
    return out, elapsed, status, n


def run_trial(client, config, command, run_id):
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=command)])]
    calls = []
    t0 = time.perf_counter()
    resp = None
    for _ in range(MAX_STEPS):
        resp = client.models.generate_content(model=MODEL, contents=contents, config=config)
        fcs = resp.function_calls or []
        if not fcs:
            break
        contents.append(resp.candidates[0].content)
        parts = []
        for fc in fcs:
            args = dict(fc.args or {})
            if fc.name in TOOLS:
                out, dt, status, n = run_tool(fc.name, args, run_id)
            else:
                out, dt, status, n = json.dumps({"status": "error", "error": "unknown tool"}), 0.0, "error", 0
            calls.append({"skill": fc.name, "args": args, "tool_sec": round(dt, 3), "api_status": status,
                          "n_results": n, "output": out})
            parts.append(types.Part.from_function_response(name=fc.name, response={"result": out}))
        contents.append(types.Content(role="user", parts=parts))
    total = time.perf_counter() - t0
    text = (resp.text or "") if resp is not None else ""
    return text, calls, total


def suggest_failure(target, calls, error, text):

    if error or not text.strip():
        return "F6"
    if not calls:
        return "F1"
    called = [c["skill"] for c in calls]
    if target not in called:
        return "F2"
    if any(c["skill"] == target and c["api_status"] in ("empty", "error") for c in calls):
        return "F3"
    return ""


FIELDS = [
    "timestamp", "system", "model", "sublevel", "cmd_id", "condition", "round", "command",
    "target_skill", "skill_called", "called_skills", "call_args", "api_status", "n_results",
    "tool_sec", "total_sec", "response", "tool_output", "failure_suggested",
    "accurate (Y/N)", "failure_type (S/F1-F6)", "notes", "run_id", "expected",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sublevel", required=True, help="e.g., 5-1, or all = every Level 5 sub-level")
    ap.add_argument("--conditions", default="E,N,P")
    ap.add_argument("--round", type=int, required=True, help="trial (round) number")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    conds = [c.strip().upper() for c in a.conditions.split(",")]
    with open(COMMANDS_CSV, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f)
                if (a.sublevel == "all" or r["sublevel"] == a.sublevel) and r["condition"] in conds]
    if not rows:
        sys.exit("No commands matched. Check --sublevel / --conditions.")

    rng = random.Random(a.seed)
    rng.shuffle(rows)


    done = set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8-sig") as f:
            for d in csv.DictReader(f):
                if d.get("system") == "Direct" and d.get("model") == MODEL and str(d.get("round")) == str(a.round):
                    done.add((d["cmd_id"], d["condition"]))
    if done:
        before = len(rows)
        rows = [r for r in rows if (r["cmd_id"], r["condition"]) not in done]
        print(f"[resume] round {a.round}: {before - len(rows)} trials already recorded, {len(rows)} left.")
        if not rows:
            print("This round is already complete. Use the next --round number.")
            return
    if a.dry_run:
        for r in rows:
            print(r["cmd_id"], r["condition"], r["command"])
        return

    client = make_client()
    config = build_config()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    new_file = not os.path.exists(a.out)

    with open(a.out, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for i, r in enumerate(rows, 1):
            run_id = uuid.uuid4().hex[:8]
            error = ""
            try:
                text, calls, total = run_trial(client, build_config(), r["command"], run_id)
            except genai_errors.ClientError as e:

                if getattr(e, "code", None) == 429 or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"\n[STOPPED] Quota error (429) after {i - 1} trials (nothing recorded for this trial).\n"
                          f"  Full message from Google:\n  {e}\n"
                          f"  The finished trials are saved. Run the same command again after the quota resets;\n"
                          f"  only the remaining trials of round {a.round} will run.")
                    sys.exit(1)
                print(f"\n[STOPPED] Setup error, nothing recorded for this trial:\n  {e}\n"
                      "Fix config.local.json (run: py baseline/check_setup.py) and run this round again.")
                sys.exit(1)
            except Exception as e:
                text, calls, total, error = "", [], 0.0, f"{type(e).__name__}: {e}"
                print(f"   error: {error[:200]}")
            target_calls = [c for c in calls if c["skill"] == r["target_skill"]]
            row = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "system": "Direct", "model": MODEL, "sublevel": r["sublevel"], "cmd_id": r["cmd_id"],
                "condition": r["condition"], "round": a.round, "command": r["command"],
                "target_skill": r["target_skill"],
                "skill_called": "Y" if target_calls else "N",
                "called_skills": ";".join(c["skill"] for c in calls),
                "call_args": json.dumps([c["args"] for c in calls], ensure_ascii=False),
                "api_status": ";".join(c["api_status"] for c in calls),
                "n_results": ";".join(str(c["n_results"]) for c in calls),
                "tool_sec": round(sum(c["tool_sec"] for c in calls), 3),
                "total_sec": round(total, 3),
                "response": text if not error else f"[ERROR] {error}",
                "tool_output": " || ".join(c["output"][:2000] for c in calls),
                "failure_suggested": suggest_failure(r["target_skill"], calls, error, text),
                "accurate (Y/N)": "", "failure_type (S/F1-F6)": "", "notes": "",
                "run_id": run_id, "expected": r["expected"],
            }
            w.writerow(row)
            f.flush()
            print(f"[{i}/{len(rows)}] {r['cmd_id']}-{r['condition']} | called={row['called_skills'] or '-'} "
                  f"| {row['total_sec']}s | {row['failure_suggested'] or 'check'}")
            time.sleep(1)


if __name__ == "__main__":
    main()
