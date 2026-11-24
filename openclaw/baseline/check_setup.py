import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills"))
import local_config

from google import genai
from google.genai import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_baseline import normalize_model

raw = os.environ.get("GEMINI_MODEL")
model = normalize_model(raw or "")
print("1) GEMINI_MODEL as written :", repr(raw))
print("   name that will be used  :", repr(model))
key = os.environ.get("GEMINI_API_KEY", "")
print("   GEMINI_API_KEY          :", f"set ({len(key)} chars)" if key else "NOT SET")

for ver in ("v1beta", "v1"):
    client = genai.Client(http_options=types.HttpOptions(api_version=ver))
    print(f"\n2) [{ver}] models containing 'pro':")
    try:
        names = sorted(m.name.replace("models/", "") for m in client.models.list())
        pro = [n for n in names if "pro" in n]
        print("   " + ("\n   ".join(pro) if pro else "(none)"))
    except Exception as e:
        print("   could not list models:", e)
    print(f"3) [{ver}] test request with '{model}':")
    try:
        r = client.models.generate_content(model=model, contents="한 단어로만 답해: 안녕")
        print("   OK ->", (r.text or "").strip())
    except Exception as e:
        print("   FAILED ->", str(e)[:1500])
