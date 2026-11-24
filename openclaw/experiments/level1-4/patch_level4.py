import os
import re
import shutil

path = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "skills",
                    "level-4", "scripts", "indirect_command.py")
raw = open(path, "rb").read()
text = raw.decode("utf-8")

if "set_autopilot(False)" in text:
    print("already patched - nothing changed")
    raise SystemExit

pattern = re.compile(r"(\r?\n)(\s*)control\.hand_brake = True(\r?\n)(\s*)self\.vehicle\.apply_control\(control\)")
m = pattern.search(text)
if not m:
    raise SystemExit("could not find the emergency_stop code - nothing changed, show this message")

shutil.copy(path, path + ".before_autopilot_fix")
nl, ind = m.group(3), m.group(4)
new = (m.group(1) + m.group(2) + "control.hand_brake = True" + nl
       + ind + "self.vehicle.set_autopilot(False)" + nl
       + ind + "self.vehicle.apply_control(control)")
text = text[:m.start()] + new + text[m.end():]
open(path, "wb").write(text.encode("utf-8"))
print("patched: level-4 emergency_stop now turns autopilot off before braking")
