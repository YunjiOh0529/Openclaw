---
name: poi-google-place
description: Search for nearby places (points of interest) such as pharmacies, cafes, gas stations, convenience stores, and restaurants using the Google Places API, and return each place's name, address, and rating. Use this when the driver asks where to find a place or service nearby.
---

# poi-google-place

Searches nearby places with the Google Places API (Text Search, New) and returns up to 5 results
within the search radius (default 1,000 m) around the vehicle's current location.

## How to run

Run from the workspace root (use `python3` instead of `python` if needed).

```bash
python skills/poi-google-place/poi_google_place.py --keyword "<place type>" --area "<landmark or area, optional>"
```

- `--keyword` (required): the type of place to find (e.g., 약국, 카페, 주유소).
- `--area` (optional): a landmark or area name (e.g., 성신여대). Leave empty to search around the current location.

## Output

JSON with `status` (`ok`, `empty`, or `error`) and `results`, each with `name`, `address`, `rating`, and `distance_m`.
Report the results to the driver in Korean, including the address and rating.
