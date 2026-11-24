import json
import os

_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.local.json")

if os.path.exists(_PATH):
    with open(_PATH, encoding="utf-8") as _f:
        for _k, _v in json.load(_f).items():
            if _v not in ("", None) and not str(_v).startswith("여기에"):
                os.environ.setdefault(_k, str(_v))
