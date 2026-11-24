# OpenClaw In-Vehicle Assistant Evaluation

Code, commands, and trial-level results for the paper "A Feasibility Study of OpenClaw Agent Framework for In-Vehicle AI Assistants" (Applied Sciences).

## Contents

| Folder | Contents |
| --- | --- |
| `skills/` | OpenClaw workspace skills (SKILL.md and Python script for each skill), the execution logger, and the user data file used by the memory skills |
| `experiments/level1-4/` | Runner for the Level 1–4 trials and the additional tests in CARLA, vehicle reset, the emergency-stop patch for the level-4 skill, and the script used for the API-failure test |
| `experiments/level5_openclaw/` | Runner for the Level 5 trials in OpenClaw and the skill-file check |
| `baseline/` | Direct function-calling baseline (same model and skills, without OpenClaw) |
| `commands/` | All test commands and the round orders |
| `results/` | Judged results of every trial |
| `analysis/` | Script that reproduces the statistics in Section 4 |
| `figures/` | Scripts for Figures 1, 3, 4, and 5 |

## Setup

1. Python 3.10 or later. Install the packages with `pip install carla==0.9.16 google-genai pandas scipy matplotlib`.
2. Copy `config.local.example.json` to `config.local.json` and fill in your own API keys. `config.local.json` is listed in `.gitignore` and must not be committed.
3. Copy the folders in `skills/` into the OpenClaw workspace (`~/.openclaw/workspace/skills/`), together with `config.local.json` placed in the workspace folder.
4. Start the CARLA 0.9.16 server and set its address in the runner scripts.

## Reproducing the results

Statistics (run from the repository root):

```
python analysis/compute_statistics.py
```

Figures:

```
python figures/make_results_figures.py
python figures/make_architecture_figure.py
dot -Tpng figures/fig_failure_trace.dot -o figures/Figure4.png
```

Running new trials:

```
python experiments/level1-4/run_level14.py --round 1
python experiments/level5_openclaw/run_openclaw.py --round 1
python baseline/run_baseline.py --sublevel all --conditions N,P --round 1
```

## Notes

- Responses and commands are in Korean, as in the experiment.
- API keys, OpenClaw session databases, and raw conversation logs are not included because they contain credentials.
