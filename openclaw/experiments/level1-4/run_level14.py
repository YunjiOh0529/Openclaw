import argparse
import csv
import datetime
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid

import carla

HOST = "210.125.91.140"
PORT = 2000
TM_PORT = 8000
MODEL = "vehicle.lincoln.mkz_2020"
SPAWN_INDEX = 0
SLOWER_PCT = 50

HERE = os.path.dirname(os.path.abspath(__file__))
COMMANDS = os.path.join(HERE, "..", "..", "commands", "level14_commands.csv")
OUT = os.path.join(HERE, "results", "level14_results.csv")
FIELDS = ["timestamp", "round", "order", "cmd_id", "level", "start", "command", "expected",
          "success (y/n)", "notes", "total_sec", "speed_before_kmh", "speed_after_kmh", "lights_after",
          "response", "session_id"]


LIGHT_FLAGS = [(0x1, "Position"), (0x2, "LowBeam(headlights)"), (0x4, "HighBeam"), (0x8, "Brake"),
               (0x10, "RightBlinker"), (0x20, "LeftBlinker"), (0x40, "Reverse"), (0x80, "Fog"),
               (0x100, "Interior")]


def lights(vehicle):
    try:
        val = int(vehicle.get_light_state())
    except Exception:
        return "unknown"
    on = [name for bit, name in LIGHT_FLAGS if val & bit]
    if val & 0x30 == 0x30:
        on.append("=> HAZARD (both blinkers)")
    return ", ".join(on) if on else "all off"


def kmh(vehicle):
    v = vehicle.get_velocity()
    return 3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)


class Sim:
    def __init__(self):
        self.client = carla.Client(HOST, PORT)
        self.client.set_timeout(60.0)
        self.world = self.client.get_world()
        self.tm = self.client.get_trafficmanager(TM_PORT)
        self.vehicle = None
        self._stop = threading.Event()
        threading.Thread(target=self._follow, daemon=True).start()

    def _follow(self):
        spectator = self.world.get_spectator()
        while not self._stop.is_set():
            try:
                if self.vehicle is not None and self.vehicle.is_alive:
                    tf = self.vehicle.get_transform()
                    back = tf.get_forward_vector() * -8.0
                    spectator.set_transform(carla.Transform(
                        carla.Location(x=tf.location.x + back.x, y=tf.location.y + back.y,
                                       z=tf.location.z + 4.0),
                        carla.Rotation(pitch=-20.0, yaw=tf.rotation.yaw)))
            except RuntimeError:
                pass
            time.sleep(0.05)

    def reset(self, start):
        old = list(self.world.get_actors().filter("vehicle.*"))
        if old:
            self.client.apply_batch_sync([carla.command.DestroyActor(a) for a in old])
        self.vehicle = None
        self.world.wait_for_tick(seconds=10.0)
        bp = self.world.get_blueprint_library().find(MODEL)
        bp.set_attribute("role_name", "ego_vehicle")
        points = self.world.get_map().get_spawn_points()
        for i in range(len(points)):
            v = self.world.try_spawn_actor(bp, points[(SPAWN_INDEX + i) % len(points)])
            if v is not None:
                break
        else:
            sys.exit("Could not spawn the vehicle.")
        self.world.wait_for_tick(seconds=10.0)
        self.vehicle = v
        v.set_light_state(carla.VehicleLightState.NONE)
        v.close_door(carla.VehicleDoor.All)
        if start == "door_open":
            v.open_door(carla.VehicleDoor.All)
            time.sleep(2.0)
            print("  car is standing still with all doors open")
        elif start == "moving":
            self.tm.vehicle_percentage_speed_difference(v, SLOWER_PCT)
            v.set_autopilot(True, TM_PORT)
            t0 = time.time()
            while kmh(v) < 8.0 and time.time() - t0 < 15:
                time.sleep(0.2)
            print(f"  car is driving on autopilot ({kmh(v):.1f} km/h)")
        else:
            time.sleep(1.0)
            print("  car is standing still")


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
        return "\n".join(p for p in (find_text(v) for v in obj) if p)
    elif isinstance(obj, str):
        return obj.strip()
    return ""


def ask(prompt, allowed=None):
    while True:
        v = input(prompt).strip()
        if allowed is None or v.lower() in allowed:
            return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--commands", default=COMMANDS, help="command list (default: level14_commands.csv)")
    ap.add_argument("--out", default=OUT, help="result file (default: results/level14_results.csv)")
    a = ap.parse_args()

    exe = shutil.which("openclaw")
    if not exe:
        sys.exit("openclaw command not found.")

    with open(a.commands, encoding="utf-8-sig") as f:
        cmds = list(csv.DictReader(f))
    random.Random(2000 + a.round).shuffle(cmds)

    done = set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8-sig") as f:
            done = {d["cmd_id"] for d in csv.DictReader(f) if str(d["round"]) == str(a.round)}
    todo = [(i, c) for i, c in enumerate(cmds, 1) if c["cmd_id"] not in done]
    if done:
        print(f"[resume] round {a.round}: {len(done)} recorded, {len(todo)} left.")
    if not todo:
        print("This round is complete.")
        return

    print("connecting to CARLA ...")
    sim = Sim()

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    new_file = not os.path.exists(a.out)
    with open(a.out, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for n, (order, c) in enumerate(todo, 1):
            print("\n" + "=" * 70)
            print(f"[{n}/{len(todo)}] round {a.round}, #{order}  {c['cmd_id']}  \"{c['command']}\"")
            print(f"  expected: {c['expected']}")
            print("  resetting vehicle ...")
            sim.reset(c["start"])
            before = kmh(sim.vehicle)

            sid = str(uuid.uuid4())
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as mf:
                mf.write(c["command"])
                msg = mf.name
            stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            t0 = time.time()
            try:
                p = subprocess.run([exe, "agent", "--session-id", sid, "--message-file", msg,
                                    "--json", "--timeout", str(a.timeout)],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                                   timeout=a.timeout + 120)
                out, err, code = p.stdout, p.stderr, p.returncode
            except subprocess.TimeoutExpired:
                out, err, code = "", "TimeoutExpired", 1
            total = time.time() - t0
            os.unlink(msg)

            if code != 0:
                print(f"\n  OpenClaw error: {(err or out).strip()[:600]}")
                print("  Nothing recorded for this trial. Fix the problem and run the same command again.")
                sys.exit(1)
            try:
                text = find_text(json.loads(out))
            except json.JSONDecodeError:
                text = out.strip()

            time.sleep(3.0)
            after = kmh(sim.vehicle) if sim.vehicle and sim.vehicle.is_alive else float("nan")
            print(f"\n  OpenClaw ({total:.1f}s):\n  " + text.replace("\n", "\n  "))
            lt = lights(sim.vehicle) if sim.vehicle and sim.vehicle.is_alive else "unknown"
            print(f"\n  speed before: {before:.1f} km/h   speed now: {after:.1f} km/h"
                  + ("   -> STOPPED" if after < 1.0 else ""))
            print(f"  lights now: {lt}")

            ok = ask("\n  Did the expected action/answer happen in CARLA? (y/n): ", {"y", "n"})
            note = ask("  Note (Enter to skip): ")
            w.writerow({"timestamp": stamp, "round": a.round, "order": order, "cmd_id": c["cmd_id"],
                        "level": c["level"], "start": c["start"], "command": c["command"],
                        "expected": c["expected"], "success (y/n)": ok.lower(), "notes": note,
                        "total_sec": round(total, 3), "speed_before_kmh": round(before, 1),
                        "speed_after_kmh": round(after, 1), "lights_after": lt, "response": text, "session_id": sid})
            f.flush()
    print(f"\nRound finished. Results: {a.out}")


if __name__ == "__main__":
    main()
