# OpenClaw In-Vehicle Assistant Evaluation

Code, test commands, and trial-level results for the paper "A Feasibility Study on the OpenClaw Agent Framework for In-Vehicle AI Assistants".

The experiment used three computers. Computer A ran the CARLA 0.9.16 simulator, Computer B ran OpenClaw with the workspace skills, and Computer C ran the direct function-calling baseline.

## Files

### `skills/`

OpenClaw workspace skills. Each skill folder has a `SKILL.md`, which the agent reads to decide when and how to use the skill, and a Python script that performs the action.

| File | Contents |
| --- | --- |
| `level-1/` | Basic vehicle control in CARLA (driving, stopping, doors, lights, turn signals, vehicle status) |
| `level-2/` | Vehicle information retrieval in CARLA (weather, position, date, day, speed) |
| `level-4/` | Situational statements mapped to vehicle actions by keyword rules (e.g., "I'm sleepy" turns on the hazard lights, stops the vehicle, and opens the doors) |
| `carla-vehicle-spawner/` | Spawns the vehicle and sets the camera view at the start of the experiment |
| `poi-google-place/poi_google_place.py` | Nearby place search with the Google Places API. Returns the name, address, and rating of the five nearest places within 1 km of the vehicle position |
| `naver-local-search/naver_news.py` | News search with the Naver News Search API. For a date such as "today" or "yesterday", keeps only articles from that day (Korean Standard Time) within the 1000 most recent articles |
| `weather-search/weather_search.py` | Current weather and 3-hour forecast for the vehicle position from the OpenWeather API |
| `lastfm-music/lastfm_music.py` | Music recommendation with the Last.fm API, either the top tracks of a named artist or tracks that match the stored preferences |
| `memory-pattern/memory_pattern.py` | Frequently visited places from the stored visit history |
| `memory-personalization/memory_personalization.py` | Stored user preferences (favorite cafe, music genres, artists). Read-only during the experiment |
| `memory_data.json` | User data prepared before the experiment (three cafes with visit counts, a favorite cafe, music genres, and artists) |
| `skill_logger.py` | Shared logger. Every skill run appends one line to `skill_log.jsonl` with the skill name, arguments, run ID, execution time, API status, and number of results. This record was used to confirm which skill was invoked |
| `local_config.py` | Loads API keys and settings from `config.local.json` into environment variables |

### `experiments/level1-4/`

Run on Computer B (OpenClaw) with CARLA running on Computer A.

| File | Contents |
| --- | --- |
| `run_level14.py` | Runs one round of the Level 1–4 commands (or the additional tests with `--commands`). For each trial it resets the vehicle to the start state, sends the command to OpenClaw in a new session, records the response, the response time, and the vehicle state before and after (speed, lights, doors), and appends one row to the result file |
| `reset_vehicle.py` | Removes all vehicles, spawns one Lincoln MKZ 2020 at a fixed spawn point, and places the camera behind it |
| `patch_level4.py` | Adds autopilot release before braking to the emergency stop of the level-4 skill, so that the stop can be observed while the vehicle drives under autopilot |
| `api_keys.py` | For the service-failure test. `break` replaces the Google Places and Naver keys in the OpenClaw workspace config with invalid values (after a backup), `restore` puts the original file back, and `status` shows the current state |

### `experiments/level5_openclaw/`

| File | Contents |
| --- | --- |
| `run_openclaw.py` | Runs one round of the 42 Level 5 utterances in OpenClaw in the fixed round order. Each trial uses a new session, measures the response time, and reads `skill_log.jsonl` to record which skills were executed |
| `check_skills.py` | Checks with MD5 checksums that the Level 5 skill files in the OpenClaw workspace are identical to the files used by the baseline. Run before each round |

### `baseline/`

Run on Computer C.

| File | Contents |
| --- | --- |
| `run_baseline.py` | Direct function-calling baseline. Gives the model the six Level 5 skills with the descriptions from their `SKILL.md`, runs the same skill scripts when the model requests a call, and returns the result to the model. Uses the same model, API key, utterances, and order as OpenClaw |
| `check_setup.py` | Checks `config.local.json`, lists the Gemini models available for the key, and sends one test request |

### `commands/`

| File | Contents |
| --- | --- |
| `level14_commands.csv` | The 25 Level 1–4 commands (Levels 1–4 and 4P) with their start states and expected behavior |
| `extra_commands.csv` | Safety, ambiguity, and multi-step commands of the additional tests (S1–S4, M1–M3) |
| `api_fail_commands.csv` | Commands of the service-failure test (A1, A2) |
| `level5_commands.csv` | The 21 Level 5 commands in Conditions N (natural) and P (paraphrased) with the requirement of each command |
| `level5_round_orders.csv` | The random order of the 42 utterances in each of the ten rounds, shared by OpenClaw and the baseline |

### `results/`

| File | Contents |
| --- | --- |
| `level14_results_final.csv` | All 125 Level 1–4 trials. `success_final` is the final judgment (response and simulator state) |
| `level5_OpenClaw_judged.csv` | All 420 Level 5 trials of OpenClaw with the invoked skills, response, skill output, response time, judgment, and failure type (F1–F6) |
| `level5_Direct_judged.csv` | All 420 Level 5 trials of the baseline in the same format |
| `extra_results_final.csv` | Trials of the safety, ambiguity, and multi-step tests |
| `apifail_results_final.csv` | Trials of the service-failure test |

### `analysis/`

| File | Contents |
| --- | --- |
| `compute_statistics.py` | Reproduces the numbers in Section 4 of the paper (success rates with Wilson confidence intervals, Fisher's exact tests with Bonferroni correction, failure types, response and skill execution times, and the additional tests) |

### `figures/`

| File | Contents |
| --- | --- |
| `make_architecture_figure.py` | Figure 1, the system architecture |
| `make_results_figures.py` | Figure 3 (outcome of each Level 1–4 trial) and Figure 5 (response time of the Level 5 trials) |
| `fig_failure_trace.dot` | Figure 4, an example of a reported action that was not performed (Graphviz) |

### Other files

| File | Contents |
| --- | --- |
| `config.local.example.json` | Template for `config.local.json` (API keys, model name, vehicle position used by the place search) |
| `.gitignore` | Keeps `config.local.json`, skill logs, and new result files out of the repository |

## Setup

1. Python 3.10 or later. Install the packages with `pip install carla==0.9.16 google-genai pandas scipy matplotlib`.
2. Copy `config.local.example.json` to `config.local.json` and fill in your own API keys. Never commit `config.local.json`.
3. Copy the folders in `skills/` and `config.local.json` into the OpenClaw workspace (`~/.openclaw/workspace/`).
4. Start the CARLA 0.9.16 server and set its address in the scripts in `experiments/level1-4/`.

## Reproducing the results

Run from the repository root.

```
python analysis/compute_statistics.py
python figures/make_results_figures.py
python figures/make_architecture_figure.py
dot -Tpng figures/fig_failure_trace.dot -o figures/Figure4.png
```

New trials:

```
python experiments/level1-4/run_level14.py --round 1
python experiments/level5_openclaw/run_openclaw.py --round 1
python baseline/run_baseline.py --sublevel all --conditions N,P --round 1
```

## Notes

- Commands and responses are in Korean, as in the experiment.
- API keys, OpenClaw session databases, and raw conversation logs are not included because they contain credentials.

# OpenClaw 차량 내 AI 비서 평가

논문 "A Feasibility Study on OpenClaw Agent Framework for In-Vehicle AI Assistants"의 코드, 테스트 명령, 시행별 결과입니다. 영어 설명은 `README.md`에 있습니다.

실험에는 컴퓨터 세 대를 사용했습니다. 컴퓨터 A는 CARLA 0.9.16 시뮬레이터, 컴퓨터 B는 워크스페이스 스킬을 설치한 OpenClaw, 컴퓨터 C는 직접 함수 호출 비교 시스템을 실행했습니다.

## 파일 설명

### `skills/`

OpenClaw 워크스페이스 스킬입니다. 각 스킬 폴더에는 `SKILL.md`와 Python 스크립트가 있습니다. `SKILL.md`는 에이전트가 언제, 어떻게 스킬을 쓸지 판단할 때 읽는 설명 파일이고, 스크립트는 실제 동작을 수행합니다.

| 파일 | 내용 |
| --- | --- |
| `level-1/` | CARLA 기본 차량 제어 (주행, 정지, 문, 조명, 방향지시등, 차량 상태) |
| `level-2/` | CARLA 차량 정보 조회 (날씨, 위치, 날짜, 요일, 속도) |
| `level-4/` | 상황 발화를 키워드 규칙으로 차량 동작에 연결 (예: "졸려"라고 하면 비상등을 켜고 정지한 뒤 문을 엶) |
| `carla-vehicle-spawner/` | 실험 시작 시 차량을 생성하고 카메라 시점을 설정 |
| `poi-google-place/poi_google_place.py` | Google Places API로 주변 장소를 검색. 차량 위치 반경 1km 안에서 가장 가까운 장소 5곳의 이름, 주소, 평점을 반환 |
| `naver-local-search/naver_news.py` | Naver 뉴스 검색 API로 뉴스를 검색. "오늘", "어제"처럼 날짜가 있으면 최근 기사 1000개 안에서 그날(한국 시간) 기사만 남김 |
| `weather-search/weather_search.py` | OpenWeather API로 차량 위치의 현재 날씨와 3시간 예보를 조회 |
| `lastfm-music/lastfm_music.py` | Last.fm API로 음악을 추천. 아티스트 이름을 말하면 그 아티스트의 인기곡을, 아니면 저장된 취향에 맞는 곡을 반환 |
| `memory-pattern/memory_pattern.py` | 저장된 방문 기록에서 자주 간 장소를 조회 |
| `memory-personalization/memory_personalization.py` | 저장된 사용자 취향(자주 가는 카페, 음악 장르, 아티스트)을 조회. 실험 중에는 읽기 전용 |
| `memory_data.json` | 실험 전에 준비한 사용자 데이터 (카페 3곳과 방문 횟수, 자주 가는 카페, 음악 장르, 아티스트) |
| `skill_logger.py` | 모든 스킬이 함께 쓰는 기록기. 스킬이 실행될 때마다 `skill_log.jsonl`에 스킬 이름, 인자, 실행 ID, 실행 시간, API 상태, 결과 수를 한 줄씩 남김. 이 기록으로 어떤 스킬이 호출됐는지 확인함 |
| `local_config.py` | `config.local.json`의 API 키와 설정을 환경 변수로 불러옴 |

### `experiments/level1-4/`

컴퓨터 A에서 CARLA를 켠 상태로 컴퓨터 B(OpenClaw)에서 실행합니다.

| 파일 | 내용 |
| --- | --- |
| `run_level14.py` | Level 1–4 명령 한 회차를 실행 (`--commands`로 추가 실험 명령도 실행 가능). 시행마다 차량을 출발 상태로 되돌리고, 새 세션으로 OpenClaw에 명령을 보낸 뒤 응답, 응답 시간, 명령 전후의 차량 상태(속도, 조명, 문)를 기록해 결과 파일에 한 줄씩 추가 |
| `reset_vehicle.py` | 모든 차량을 지우고 정해진 위치에 Lincoln MKZ 2020 한 대를 생성한 뒤 카메라를 차 뒤에 배치 |
| `patch_level4.py` | level-4 스킬의 비상정지 기능에 "제동 전에 자동주행 해제"를 추가. 자동주행 중인 차량에서 정지를 확인하기 위해 사용 |
| `api_keys.py` | 서비스 실패 실험용. `break`는 OpenClaw 설정 파일을 백업한 뒤 Google Places와 Naver 키를 무효 값으로 바꾸고, `restore`는 원래 파일로 되돌리며, `status`는 현재 상태를 보여 줌 |

### `experiments/level5_openclaw/`

| 파일 | 내용 |
| --- | --- |
| `run_openclaw.py` | Level 5 발화 42개 한 회차를 정해진 순서로 OpenClaw에서 실행. 시행마다 새 세션을 쓰고, 응답 시간을 재고, `skill_log.jsonl`을 읽어 실제로 실행된 스킬을 기록 |
| `check_skills.py` | OpenClaw 워크스페이스의 Level 5 스킬 파일이 비교 시스템과 같은지 MD5 체크섬으로 확인. 매 회차 전에 실행 |

### `baseline/`

컴퓨터 C에서 실행합니다.

| 파일 | 내용 |
| --- | --- |
| `run_baseline.py` | 직접 함수 호출 비교 시스템. 모델에 Level 5 스킬 6개를 각 `SKILL.md`의 설명과 함께 주고, 모델이 호출을 요청하면 같은 스킬 스크립트를 실행해 결과를 돌려줌. OpenClaw와 같은 모델, API 키, 발화, 순서를 사용 |
| `check_setup.py` | `config.local.json` 설정을 확인하고, 키로 쓸 수 있는 Gemini 모델 목록을 보여 준 뒤 테스트 요청을 한 번 보냄 |

### `commands/`

| 파일 | 내용 |
| --- | --- |
| `level14_commands.csv` | Level 1–4 명령 25개(Level 1–4, 4P)와 각 명령의 출발 상태, 기대 동작 |
| `extra_commands.csv` | 추가 실험의 안전·모호성·다단계 명령 (S1–S4, M1–M3) |
| `api_fail_commands.csv` | 서비스 실패 실험 명령 (A1, A2) |
| `level5_commands.csv` | Level 5 명령 21개의 N(자연스러운 요청), P(돌려 말한 요청) 두 조건과 명령별 요구사항 |
| `level5_round_orders.csv` | 10회차 각각의 발화 42개 무작위 순서. OpenClaw와 비교 시스템이 같은 순서를 사용 |

### `results/`

| 파일 | 내용 |
| --- | --- |
| `level14_results_final.csv` | Level 1–4 시행 125회 전체. `success_final`이 최종 판정(응답과 시뮬레이터 상태 기준) |
| `level5_OpenClaw_judged.csv` | OpenClaw의 Level 5 시행 420회 전체. 호출된 스킬, 응답, 스킬 출력, 응답 시간, 판정, 실패 유형(F1–F6) 포함 |
| `level5_Direct_judged.csv` | 비교 시스템의 Level 5 시행 420회 전체 (같은 형식) |
| `extra_results_final.csv` | 안전·모호성·다단계 실험 시행 |
| `apifail_results_final.csv` | 서비스 실패 실험 시행 |

### `analysis/`

| 파일 | 내용 |
| --- | --- |
| `compute_statistics.py` | 논문 4장의 수치를 재현 (Wilson 신뢰구간을 포함한 성공률, Bonferroni 보정한 Fisher 정확검정, 실패 유형, 응답 시간과 스킬 실행 시간, 추가 실험 결과) |

### `figures/`

| 파일 | 내용 |
| --- | --- |
| `make_architecture_figure.py` | 그림 1, 시스템 구조 |
| `make_results_figures.py` | 그림 3(Level 1–4 시행별 결과)과 그림 5(Level 5 응답 시간) |
| `fig_failure_trace.dot` | 그림 4, 수행하지 않은 동작을 보고한 사례 (Graphviz) |

### 기타 파일

| 파일 | 내용 |
| --- | --- |
| `config.local.example.json` | `config.local.json` 양식 (API 키, 모델 이름, 장소 검색에 쓰는 차량 위치) |
| `.gitignore` | `config.local.json`, 스킬 기록, 새 결과 파일이 저장소에 올라가지 않게 함 |

## 설치

1. Python 3.10 이상. `pip install carla==0.9.16 google-genai pandas scipy matplotlib`로 패키지를 설치합니다.
2. `config.local.example.json`을 `config.local.json`으로 복사하고 본인의 API 키를 입력합니다. `config.local.json`은 절대 커밋하지 마세요.
3. `skills/` 안의 폴더들과 `config.local.json`을 OpenClaw 워크스페이스(`~/.openclaw/workspace/`)에 복사합니다.
4. CARLA 0.9.16 서버를 켜고, `experiments/level1-4/`의 스크립트에 서버 주소를 설정합니다.

## 결과 재현

저장소 최상위 폴더에서 실행합니다.

```
python analysis/compute_statistics.py
python figures/make_results_figures.py
python figures/make_architecture_figure.py
dot -Tpng figures/fig_failure_trace.dot -o figures/Figure4.png
```

새 시행을 실행할 때는 다음과 같습니다.

```
python experiments/level1-4/run_level14.py --round 1
python experiments/level5_openclaw/run_openclaw.py --round 1
python baseline/run_baseline.py --sublevel all --conditions N,P --round 1
```

## 참고

- 명령과 응답은 실험과 같이 한국어입니다.
- API 키, OpenClaw 세션 데이터베이스, 대화 기록 원본은 인증 정보가 들어 있어 포함하지 않았습니다.
