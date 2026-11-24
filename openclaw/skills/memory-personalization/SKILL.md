---
name: memory-personalization
description: Read or remember the driver's personal preferences stored in local memory, such as favorite cafe (favorite_cafe), favorite artists (favorite_artists), and preferred music genres (music_genres). Use this when the driver asks about their own preferences or asks the assistant to remember one.
---

# memory-personalization

Reads (and, outside experiments, updates) the preferences in `skills/memory_data.json`.

## How to run

Run from the workspace root (use `python3` instead of `python` if needed).

```bash
python skills/memory-personalization/memory_personalization.py --action get --key "<key, optional>"
python skills/memory-personalization/memory_personalization.py --action set --key "<key>" --value "<value>"
```

Keys: `favorite_cafe`, `favorite_artists`, `music_genres`. Without `--key`, all preferences are returned.

## Output

JSON with `status` and `results`. Answer the driver in Korean.
During experiments the memory is read-only, so `set` returns `status: readonly`.
