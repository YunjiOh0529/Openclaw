---
name: memory-pattern
description: Recommend places the driver visits frequently, based on the visit history stored in local memory, optionally filtered by category (e.g., 카페), with the number of visits for each place. Use this when the driver asks about places they often go to or usually visit.
---

# memory-pattern

Reads the visit history in `skills/memory_data.json` and returns the most visited places.

## How to run

Run from the workspace root (use `python3` instead of `python` if needed).

```bash
python skills/memory-pattern/memory_pattern.py --category "<category, optional>" --top <number, optional, default 3>
```

## Output

JSON with `status` and `results`, each with `place`, `category`, `visits`, and `last_visit`.
Recommend the places to the driver in Korean, most visited first.
