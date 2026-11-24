---
name: naver-local-search
description: Search recent Korean news articles with the Naver News Search API by topic or keyword (e.g., 스포츠, 경제, IT) and an optional date (YYYY-MM-DD), and return the title, summary, link, and publication time of each article. Use this when the driver asks about news or current events.
---

# naver-local-search

Searches Naver News, newest first, and returns up to 5 articles.
If a date is given, only articles published on that date (Korea time) are returned.

## How to run

Run from the workspace root (use `python3` instead of `python` if needed).

```bash
python skills/naver-local-search/naver_news.py --query "<topic or keyword>" --date "<YYYY-MM-DD, optional>"
```

## Output

JSON with `status` (`ok`, `empty`, or `error`) and `results`, each with `title`, `summary`, `link`, and `published`.
Summarize the articles for the driver in Korean.
