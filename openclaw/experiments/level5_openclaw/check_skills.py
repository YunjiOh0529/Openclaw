import hashlib
import os

WS = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace")
EXPECTED = {
    "skills/skill_logger.py": "e15e8aadcfe445cd0b77dc446911c832",
    "skills/local_config.py": "4cd8b7ca1210337e2b0c6a31864c8b43",
    "skills/memory_data.json": "898b78cf497e79824407948e232968cf",
    "skills/lastfm-music/SKILL.md": "7e466b316b798351be7779313264ab68",
    "skills/memory-pattern/SKILL.md": "8acc1cbeb9b5838ee011f989225191cb",
    "skills/memory-personalization/SKILL.md": "0a3b075f84728d5eb43c5a988cfb2f34",
    "skills/naver-local-search/SKILL.md": "afef3f816b394a7f41c5a53b9ab17356",
    "skills/poi-google-place/SKILL.md": "11641d35d9498dbbd8257651978a1fc5",
    "skills/weather-search/SKILL.md": "7d025b8e8b39a10a826edade00e2e656",
    "skills/lastfm-music/lastfm_music.py": "6caeab07286202b57895eb4c786c1cdb",
    "skills/memory-pattern/memory_pattern.py": "2a23ea261dd3aa05f5d763d1338d5f97",
    "skills/memory-personalization/memory_personalization.py": "85c7a3df72f84d86fb29299fc817367e",
    "skills/naver-local-search/naver_news.py": "91b8304c8720f12e3f82b27b38450907",
    "skills/poi-google-place/poi_google_place.py": "e71a79e07ae7a573df812a0dbe0c58d6",
    "skills/weather-search/weather_search.py": "671443919ff932dda7b0d3da2cdace6e",
}

bad = 0
for rel, want in EXPECTED.items():
    path = os.path.join(WS, *rel.split("/"))
    if not os.path.exists(path):
        print(f"MISSING  {rel}")
        bad += 1
        continue
    data = open(path, "rb").read().replace(b"\r", b"").rstrip() + b"\n"
    got = hashlib.md5(data).hexdigest()
    if got != want:
        print(f"CHANGED  {rel}")
        bad += 1
    else:
        print(f"ok       {rel}")

extra = [d for d in os.listdir(os.path.join(WS, "skills"))
         if os.path.isdir(os.path.join(WS, "skills", d))]
print("\nskill folders:", ", ".join(sorted(extra)))
print("\nALL OK" if bad == 0 else f"\n{bad} PROBLEM(S) - do not start the round; show this output.")
