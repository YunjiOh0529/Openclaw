import argparse
import datetime
import email.utils
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import local_config
import skill_logger

LOG = skill_logger.start("naver-local-search")
URL = "https://openapi.naver.com/v1/search/news.json"
KST = datetime.timezone(datetime.timedelta(hours=9))
MAX_RESULTS = 5


def clean(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def fetch(query, start):
    params = urllib.parse.urlencode({"query": query, "display": 100, "start": start, "sort": "date"})
    req = urllib.request.Request(f"{URL}?{params}", headers={
        "X-Naver-Client-Id": os.environ["NAVER_CLIENT_ID"],
        "X-Naver-Client-Secret": os.environ["NAVER_CLIENT_SECRET"],
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8")).get("items", [])


def search(query, date=""):


    results = []
    pages = range(1, 1000, 100) if date else [1]
    for start in pages:
        items = fetch(query, start)
        if not items:
            break
        older = False
        for it in items:
            pub = email.utils.parsedate_to_datetime(it.get("pubDate")).astimezone(KST)
            day = pub.strftime("%Y-%m-%d")
            if date and day != date:
                older = older or day < date
                continue
            results.append({
                "title": clean(it.get("title")),
                "summary": clean(it.get("description")),
                "link": it.get("originallink") or it.get("link"),
                "published": pub.strftime("%Y-%m-%d %H:%M"),
            })
        LOG["pages"] = start // 100 + 1
        if len(results) >= MAX_RESULTS or older:
            break
    return results[:MAX_RESULTS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--date", default="")
    a = ap.parse_args()
    LOG["query"], LOG["date"] = a.query, a.date
    try:
        results = search(a.query, a.date.strip())
        status = "ok" if results else "empty"
        out = {"status": status, "query": a.query, "date": a.date, "results": results}
    except (urllib.error.URLError, KeyError, ValueError, TypeError) as e:
        status = "error"
        out = {"status": status, "error": str(e), "results": []}
    LOG["api_status"], LOG["n_results"] = status, len(out["results"])
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
