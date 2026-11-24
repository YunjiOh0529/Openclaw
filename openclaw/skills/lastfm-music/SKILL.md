---
name: lastfm-music
description: Recommend music with the Last.fm API, either popular tracks by a specific artist (mode=artist) or tracks matching the driver's stored music taste (mode=taste). Use this when the driver asks for song or music recommendations.
---

# lastfm-music

## How to run

Run from the workspace root (use `python3` instead of `python` if needed).

```bash
python skills/lastfm-music/lastfm_music.py --mode artist --artist "<artist name>"
python skills/lastfm-music/lastfm_music.py --mode taste
```

- `artist`: top tracks of the given artist.
- `taste`: tracks for the driver's preferred genres and artists similar to their favorite artists, read from `skills/memory_data.json`.

## Output

JSON with `status` and `results` (track `title` and `artist`). Recommend the songs to the driver in Korean.
