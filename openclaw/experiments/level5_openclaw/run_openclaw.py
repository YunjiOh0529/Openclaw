import argparse
import csv
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ORDERS = os.path.join(HERE, "..", "..", "commands", "level5_round_orders.csv")
DEFAULT_WS = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace")
DEFAULT_OUT = os.path.join(HERE, "results", "openclaw_results.csv")
MODEL = "gemini-3.1-pro-preview"

FIELDS = ["timestamp", "system", "model", "sublevel", "cmd_id", "condition", "round", "command",
          "target_skill", "skill_called", "called_skills", "call_args", "api_status", "n_results",
          "tool_sec", "total_sec", "response", "tool_output", "failure_suggested",
          "accurate (Y/N)", "failure_type (S/F1-F6)", "notes", "run_id", "expected"]

STOP_WORDS = ["RESOURCE_EXHAUSTED", "429", "402", "quota", "prepayment credits", "rate limit"]


def read_log(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def find_text(obj):

    if isinstance(obj, dict):
        for key in ("reply", "text", "outputText", "message", "content", "result", "payloads"):
            if key in obj:
                t = find_text(obj[key])
                if t:
                    return t
        for v in obj.values():
            t = find_text(v)
            if t:
                return t
    elif isinstance(obj, list):
        parts = [find_text(v) for v in obj]
        parts = [p for p in parts if p]
        return "\n".join(parts)
    elif isinstance(obj, str):
        return obj.strip()
    return ""


def suggest_failure(target, calls, error, text):
    if error or not text:
        return "F6"
    if not calls:
        return "F1"
    tcalls = [c for c in calls if c.get("skill") == target]
    if not tcalls:
        return "F2"
    if all(c.get("api_status") in ("empty", "error", None, "") for c in tcalls):
        return "F3"
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--workspace", default=DEFAULT_WS)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--limit", type=int, default=0, help="run only the first N remaining trials (test)")
    ap.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args()

    exe = shutil.which("openclaw")
    if not exe:
        sys.exit("openclaw command not found. Run this in the PowerShell where `openclaw` works.")
    log_path = os.path.join(a.workspace, "skills", "skill_log.jsonl")

    with open(ORDERS, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if int(r["round"]) == a.round]
    rows.sort(key=lambda r: int(r["order"]))

    done = set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8-sig") as f:
            for d in csv.DictReader(f):
                if str(d.get("round")) == str(a.round):
                    done.add((d["cmd_id"], d["condition"]))
    todo = [r for r in rows if (r["cmd_id"], r["condition"]) not in done]
    if done:
        print(f"[resume] round {a.round}: {len(done)} trials already recorded, {len(todo)} left.")
    if a.limit:
        todo = todo[:a.limit]
    if not todo:
        print("Nothing to run for this round.")
        return

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    raw_dir = os.path.join(os.path.dirname(a.out), "openclaw_raw")
    os.makedirs(raw_dir, exist_ok=True)
    new_file = not os.path.exists(a.out)

    with open(a.out, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for i, r in enumerate(todo, 1):
            sid = str(uuid.uuid4())
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as mf:
                mf.write(r["command"])
                msg_path = mf.name
            n_before = len(read_log(log_path))
            t0 = time.time()
            stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                p = subprocess.run([exe, "agent", "--session-id", sid, "--message-file", msg_path,
                                    "--json", "--timeout", str(a.timeout)],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   timeout=a.timeout + 120)
                out, err, code = p.stdout, p.stderr, p.returncode
            except subprocess.TimeoutExpired:
                out, err, code = "", "TimeoutExpired", 1
            total = time.time() - t0
            os.unlink(msg_path)
            time.sleep(2)
            new_logs = read_log(log_path)[n_before:]

            with open(os.path.join(raw_dir, f"r{a.round}_{r['order']}_{r['cmd_id']}-{r['condition']}.json"),
                      "w", encoding="utf-8") as rf:
                rf.write(out or "")
                if err:
                    rf.write("\n\n--- stderr ---\n" + err)

            error = ""
            text = ""
            if code != 0:
                blob = (out or "") + (err or "")
                if any(s.lower() in blob.lower() for s in STOP_WORDS):
                    print(f"\n[STOPPED] Quota / credit error after {i - 1} trials. Nothing recorded for this trial.\n"
                          f"  Message: {blob.strip()[:800]}\n"
                          f"  Run the same command again later; only the remaining trials will run.")
                    sys.exit(1)
                error = (err or out or "unknown error").strip()[:500]
            else:
                try:
                    text = find_text(json.loads(out))
                except json.JSONDecodeError:
                    text = out.strip()

            calls = [{"skill": g.get("skill", ""), "args": g.get("args", ""),
                      "api_status": g.get("api_status", ""), "n_results": g.get("n_results", ""),
                      "sec": g.get("duration_sec", 0) or 0} for g in new_logs]
            row = {
                "timestamp": stamp, "system": "OpenClaw", "model": MODEL,
                "sublevel": r["sublevel"], "cmd_id": r["cmd_id"], "condition": r["condition"],
                "round": a.round, "command": r["command"], "target_skill": r["target_skill"],
                "skill_called": "Y" if any(c["skill"] == r["target_skill"] for c in calls) else "N",
                "called_skills": ";".join(c["skill"] for c in calls),
                "call_args": json.dumps([c["args"] for c in calls], ensure_ascii=False),
                "api_status": ";".join(str(c["api_status"]) for c in calls),
                "n_results": ";".join(str(c["n_results"]) for c in calls),
                "tool_sec": round(sum(float(c["sec"]) for c in calls), 3),
                "total_sec": round(total, 3),
                "response": text if not error else f"[ERROR] {error}",
                "tool_output": "",
                "failure_suggested": suggest_failure(r["target_skill"], calls, error, text),
                "accurate (Y/N)": "", "failure_type (S/F1-F6)": "", "notes": "",
                "run_id": sid, "expected": r["expected"],
            }
            w.writerow(row)
            f.flush()
            print(f"[{i}/{len(todo)}] {r['cmd_id']}-{r['condition']} | called={row['called_skills'] or '-'} "
                  f"| {row['total_sec']}s | {row['failure_suggested'] or 'check'}")
            time.sleep(1)


if __name__ == "__main__":
    main()
